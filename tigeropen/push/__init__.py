# -*- coding: utf-8 -*-
"""
Created on 2018/10/29

@author: gaoan
"""
import ssl
import time


def _patch_ssl(wait=0.01):
    def new_wrap_socket(self, sock, server_side=False,
                        do_handshake_on_connect=True,
                        suppress_ragged_eofs=True,
                        server_hostname=None, session=None):
        time.sleep(wait)
        return self.sslsocket_class._create(
            sock=sock,
            server_side=server_side,
            do_handshake_on_connect=do_handshake_on_connect,
            suppress_ragged_eofs=suppress_ragged_eofs,
            server_hostname=server_hostname,
            context=self,
            session=session
        )
    ssl.SSLContext.old_wrap_socket = ssl.SSLContext.wrap_socket
    ssl.SSLContext.wrap_socket = new_wrap_socket

