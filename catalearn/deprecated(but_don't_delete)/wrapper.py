from .color_print import color_print
import dill
import inspect
from .local_params import get_local_vars
from .reindent import correct_indentation

def get_source(func):
	raw_source = inspect.getsource(func)
	print(raw_source)
	corrected_source = correct_indentation(raw_source)
	print(corrected_source)
	return corrected_source

class Wrapper():

	def __init__(self, connector):
		self.connector = connector


	def wrap(self, func):

		def wrapped_func(*args):

			gpu_hash, gpu_ip, ws_port = self.connector.contact_server()

			if (gpu_hash is None or gpu_ip is None or ws_port is None):
				return

			source = get_source(func)
			params = get_local_vars(source, 4)

			uploads = {}
			uploads['function'] = func
			uploads['variables'] = args
			uploads['env'] = params

			with open('uploads.pkl', 'wb') as file:
				dill.dump(uploads, file)

			self.connector.upload_params_decorator(gpu_ip, gpu_hash)
			outUrl = self.connector.stream_output(gpu_ip, gpu_hash, ws_port)

			if outUrl is None:
				color_print('computation failed')
				return 

			result = self.connector.get_return_object(outUrl)
			return result

		return wrapped_func