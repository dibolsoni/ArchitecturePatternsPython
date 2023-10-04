import logging
import smtplib

import config
from adapters.notification.notification import AbstractNotification

DEFAULT_HOST = config.EMAIL.HOST
DEFAULT_PORT = config.EMAIL.PORT

logger = logging.getLogger(__name__)


class EmailNotification(AbstractNotification):
	def __init__(self, smtp_host=DEFAULT_HOST, port=DEFAULT_PORT):
		logger.info(f'connecting to {smtp_host}:{port}')
		self.server = smtplib.SMTP(smtp_host, port=port)
		self.server.noop()

	def send(self, destination: str, message: str):
		msg = f'Subject: allocation service notification\n{message}'
		self.server.sendmail(
			from_addr="allocation@example.com",
			to_addrs=[destination],
			msg=msg
		)
