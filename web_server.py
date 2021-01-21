from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import os
import urllib
import shutil
import re
import io
from io import StringIO
import html


class RequestHandler(BaseHTTPRequestHandler):
   
    def get_file(self):
        # Sends reponse code and a file object which has to be copied to the output file
        path = self.path
        path = self.get_current_path(self.path)
        fptr = None
        if os.path.isdir(path):
            return self.list_directory(path)
        #Select the type of a file. For now I have added just 'text'
        ctype = 'text/plain'
        print(self.path, path)
        try:
            # Reading file in binary mode as text mode can have newline translation
            fptr = open(path, 'rb')
        except IOError:    
            #Handle Error
            self.send_error(404, "File not found at " +path)
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(fptr.fileno())
        # fstat returns the status of the file descriptor and we want size of the content i.e fs[6]
        self.send_header("Content-Length", str(fs[6]))
        # time of most recent content modification
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return fptr

    def do_GET(self):
        #Overriding do_GET method of the base handler just to add the functionality of serving file
        print(threading.currentThread().getName().encode() + b'\t' + str(threading.active_count()).encode() + b'\n')
        fptr = self.get_file()
        if fptr:
            #Copy the data of two file objects where source is for reading
            #and outputfile is for writing
            # wfile contains the output stream for writing a response back to the client
            shutil.copyfileobj(fptr, self.wfile)
            fptr.close()
        return 
    
    def get_current_path(self, path):
        # '/fs/' => '/'
        # '/fs/home/' => '/home/'
        # Translate a /-separated PATH to the local filename syntax except directories

        #Checks for query params and ignore
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        #Split for file name
        words = path.split('/')
        words = filter(None, words)
        #Get current working directory path
        path = os.getcwd()     
        for word in words:
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def list_directory(self, path):
        '''
        @param path 
        @return file object
        '''
        # Display directory listing just like the http.server default page
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        list = ['..'] + list
        fptr = StringIO()
        # Get url
        displaypath = html.escape(urllib.parse.unquote(self.path))
        # Create Dynamic HTML
        fptr.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        fptr.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        fptr.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        fptr.write("<hr>\n")
        fptr.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        fptr.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            fptr.write('<li><a href="%s">%s</a>\n'
                    % (urllib.parse.quote(linkname), html.escape(displayname)))
        fptr.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = fptr.tell()
        fptr.seek(0)
        byteio = io.BytesIO(fptr.read().encode('utf8'))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()

        return byteio

#Since http.server is single threaded, need to make it multithreaded to run mutiple requests
class ThreadServer(ThreadingMixIn, HTTPServer):
    pass    

def run():
    server = ThreadServer(('0.0.0.0', 4445), RequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    run()
