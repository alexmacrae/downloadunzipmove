import urllib2
import os
import zipfile
import shutil

tmp_dir = "./tmp/"
downloaded_dir = "./downloaded/"
if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)
if not os.path.exists(downloaded_dir): os.makedirs(downloaded_dir)


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 0)
    print "Downloaded %d of %d bytes (%d%%)\r" % (bytes_so_far, total_size, percent)
    if bytes_so_far >= total_size:
        print 'Download complete'



def chunk_read(file_response, file_url, chunk_size=8192, report_hook=None):

    filename = file_url.split('/')[-1]


    # Check to see if sample set has already been downloaded and extracted to the destination dir
    if os.path.exists(downloaded_dir + filename.split('.')[-2]):
        print 'Already downloaded. Do nothing.'
    else:

        file_path = tmp_dir + filename
        f = open(file_path, 'wb')

        try:
            total_size = file_response.info().getheader('Content-Length').strip()
            header = True
        except AttributeError:
            header = False  # a response doesn't always include the "Content-Length" header

        if header:
            total_size = int(total_size)

        bytes_so_far = 0

        while True:
            chunk = file_response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not header:
                total_size = bytes_so_far  # unknown size

            if not chunk:
                break

            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)

            f.write(chunk) # write chunk to file

        # finished downloading
        f.close()
        unzip(file_path, filename)


def unzip(file_path, filename):
    new_dir_name = filename.split('.')[-2]
    extracted_dir_path = tmp_dir + 'extracted/' + new_dir_name

    if not os.path.exists(extracted_dir_path): os.makedirs(extracted_dir_path)

    downloaded_zip_file = zipfile.ZipFile(file_path, 'r')
    downloaded_zip_file.extractall(extracted_dir_path)
    downloaded_zip_file.close()
    try:
        move_extracted_dir(extracted_dir_path, new_dir_name)
    except:
        print 'Directory already exists. Removing tmp files.'
        shutil.rmtree(extracted_dir_path) # delete tmp extracted dir and all its contents
        pass
    os.remove(file_path) # delete the zip

def move_extracted_dir(extracted_dir_path, new_dir_name):
    new_dir_path = downloaded_dir + new_dir_name
    os.rename(extracted_dir_path, new_dir_path)


if __name__ == '__main__':
    file_url = 'http://www.samplerbox.org/files/instruments/0Saw.zip'
    file_response = urllib2.urlopen(file_url)
    chunk_read(file_response, file_url, report_hook=chunk_report)
