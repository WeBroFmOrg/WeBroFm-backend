import msgpack
from rest_framework.renderers import BaseRenderer

class MessagePackRenderer(BaseRenderer):
    media_type = 'application/x-msgpack'
    format = 'msgpack'
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b''
        return msgpack.packb(data, use_bin_type=True)
