import logging
import os
import shlex
import subprocess
import time

import requests
from celery.decorators import task
from django.core.mail import EmailMessage
from requests_html import HTMLSession

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

    name = r.html.xpath('//div/h1/text()')[0].strip().title()
    author = r.html.xpath('//strong/a/text()')[0]

    urls = r.html.xpath('//ul[@class="table-of-contents"]/li/a/@href')
    links = [BASE_URL + url for url in urls]

    return name, author, links


def crawl_chap(link):
    paragraphs = []

    session = HTMLSession()
    r = session.get(link)

    title = r.html.xpath('//header/h2/text()')[0].strip()
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
    time.sleep(40)
    logger.info('Generated MOBI file successfully', extra=d)


def remove_html_file(name):
    try:
        os.remove(name + '.html')
        os.remove(name + '.mobi')
    except FileNotFoundError:
        pass


def send_email(name, email):
    from_ = 'dosontung987@gmail.com'
    to = email
    subject = name + '.mobi'

    logger.info('Sending email to %s', to, extra=d)

    email_subj = EmailMessage('Your ebook which generate in WattpadEbook',
                              'Thanks for using our service',
                              from_, [to])
    email_subj.content_subtype = 'html'
    email_subj.attach_file(subject)
    email_subj.send()

    logger.info('Sent email successfully', extra=d)
    time.sleep(0.01)


def link_is_vaild(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'}
    if url.startswith('https://www.wattpad.com/') and requests.head(url, headers=headers).ok:
        return True
    else:
        return False


def link_not_vaild(output_profile, email):
    content = 'Link invaild'
    with open('link_invaild', 'w') as f:
        f.write(content)
    generate_mobi_file('link_invaild', 'WattpadEbook', output_profile)

    from_ = 'dosontung987@gmail.com'
    to = email
    subject = 'link_not_vaild.mobi'

    logger.info('Sending email to %s', to, extra=d)

    email_subj = EmailMessage('Your link which you type in WattpadEbook isn\'t vaild',
                              'Please try again',
                              from_, [to])
    email_subj.content_subtype = 'html'
    email_subj.attach_file(subject)
    email_subj.send()

    logger.info('Sent email successfully', extra=d)
    try:
        os.remove('link_not_vaild.html')
        os.remove('link_not_vaild.mobi')
    except FileNotFoundError:
        pass

    time.sleep(0.01)



@task(name="generate_ebook")
def make_story(url, profile, email):
    if link_is_vaild(url):
        name, author, links = crawl_all_chaps(url)
        name = name.replace('/', '-')

        generate_html_file(links, name)
        generate_mobi_file(name, author, profile)
        send_email(name, email)
        remove_html_file(name)
    else:
        link_not_vaild(profile, email)
