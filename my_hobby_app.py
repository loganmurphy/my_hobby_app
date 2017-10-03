import os
import boto3

import tornado.ioloop
import tornado.web
import tornado.log

from dotenv import load_dotenv

from jinja2 import Environment, PackageLoader, select_autoescape

load_dotenv('.env')

PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

SES_CLIENT = boto3.client(
    'ses',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name="us-west-2"
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get(self):
    self.set_header("Content-Type", 'html')
    self.render_template('index.html', {})
    # self.render_template('index.html', {'path': self.request.path})

class PageHandler(TemplateHandler):
  def post(self, page):
      email = self.get_body_argument('email')
      first_name = self.get_body_argument('first_name')
      last_name = self.get_body_argument('last_name')
      response = SES_CLIENT.send_email(
        Destination={
          'ToAddresses': ['loganmurphy1984@gmail.com'],
        },
        Message={
          'Body': {
            'Text': {
              'Charset': 'UTF-8',
              'Data': 'Email: {}\nName: {}, {}\n'.format(email, last_name, first_name)
            },
          },
          'Subject': {'Charset': 'UTF-8', 'Data': 'Thank You!'},
        },
        Source='loganmurphy1984@gmail.com'
      )
      self.redirect('/page/thank-you-for-submitting.html')
  def get(self, page):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {})
    # self.render_template(name, {'path': self.request.path})

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/page/(.*)", PageHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'})
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()

  app = make_app()
  app.listen(PORT, print("Server started on localhost:" + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
