import os

import tornado.ioloop
import tornado.web
import tornado.log

from jinja2 import Environment, PackageLoader, select_autoescape

PORT = int(os.environ.get('PORT', '8888'))

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class HomeHandler(TemplateHandler):
  def get(self):
    self.set_header("Content-Type", 'html')
    self.render_template('index.html', {})
    # self.render_template('index.html', {'path': self.request.path})

class PageHandler(TemplateHandler):
  def get(self, name):
    self.render_template(name, {})
    # self.render_template(name, {'path': self.request.path})

def make_app():
  return tornado.web.Application([
    (r"/", HomeHandler),
    (r"/page/(.*)", PageHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'})
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()

  app = make_app()
  app.listen(PORT, print("Server started on localhost:" + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
