import os
import shlex
import smtplib
import subprocess
import time

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from requests_html import HTMLSession
from celery.decorators import task
import logging


BASE_URL = 'https://www.wattpad.com'

FORMAT = '%(asctime)-15s: %(user)-8s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger(__name__)
d = {
     'user': os.getenv('USERNAME')
     }


def crawl_all_chaps(link):
    session = HTMLSession()
    r = session.get(link)

    name = r.html.xpath('//span/h1/text()')[0].strip().title()
    author = r.html.xpath('//div[@class="author hidden-lg"]/a[2]/text()')[0]

    urls = r.html.xpath('//ul[@class="table-of-contents"]/li/a/@href')
    links = [BASE_URL + url for url in urls]

    return name, author, links


def crawl_chap(link):
    paragraphs = []

    session = HTMLSession()
    r = session.get(link)

    title = r.html.xpath('//h2/text()')[0].strip()
    page = 1
    logger.info('Crawling chap %s', title, extra=d)

    while True:
        r = session.get(link + '/page/{}'.format(page))
        paragraph = r.html.xpath('//pre//p/text()')
        if paragraph:
            paragraphs.append('<br>'.join(paragraph))
            page += 1
        else:
            break

    content = '<br>'.join(paragraphs)
    logger.info('Crawled chap %s successfully', title.strip(), extra=d)
    return title, content


def generate_html_file(links, name):
    logger.info('Generating HTML file', extra=d)

    content_chaps = []
    html_tpl = """<h2 style="text-align:center;">
                      {}
                  </h2>
                  <br><br>
                  <p>
                    {}
                  </p>
                  <br><br><br>
               """

    for link in links:
        chap_title, chap_content = crawl_chap(link)
        content_chaps.append(html_tpl.format(chap_title, chap_content))

    content = '\n'.join(content_chaps)

    with open('{}.html'.format(name), 'w') as f:
        f.write(content)


def generate_mobi_file(name, author, output_profile):
    cmd_tpl = (
        'ebook-convert "{name}.html" "{name}.mobi" '
        '--output-profile {profile} --level1-toc //h:h2 '
        '--authors "{author}" --title "{name}"'
    )
    logger.info('Generating MOBI file', extra=d)
    cmd = cmd_tpl.format(name=name, profile=output_profile,
                         author=author)

    subprocess.Popen(shlex.split(cmd))
    time.sleep(10)
    logger.info('Generated MOBI file successfully', extra=d)


def remove_html_file(name):
    filename = name + '.mobi'
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


def send_email(name, email):
    from_ = os.getenv('GMAIL_USERNAME')
    to = email
    subject = name + '.mobi'

    logger.info('Sending email to %s', to, extra=d)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(from_, os.getenv('GMAIL_PASSWORD'))

    msg = MIMEMultipart()

    msg['From'] = from_
    msg['To'] = to
    msg['Subject'] = subject

    filename = subject
    attachment = open(subject, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment", filename=filename)
    msg.attach(part)

    text = msg.as_string()
    server.sendmail(from_, to, text)
    server.quit()
    attachment.close()
    logger.info('Sent email successfully', extra=d)


@task(name="generate_ebook")
def make_story(url, profile, email):
    name, author, links = crawl_all_chaps(url)
    name = name.replace('/', '-')

    generate_html_file(links, name)
    generate_mobi_file(name, author, profile)
    remove_html_file(name)
    send_email(name, email)
