#!/usr/bin/env python

# uploadr.py inspired by http://berserk.org/uploadr/
# but using http://stuvel.eu/projects/flickrapi instead

import sys, time, os, shelve, string
import exifread
import flickrapi

#
# Location to scan for new images
#   
IMAGE_DIR = "/Volumes/NIKON D40"

#
#   Flickr settings
#
FLICKR = {"title": "",
        "description": "",
        "tags": "autoupload",
        "is_public": "0",
        "is_friend": "0",
        "is_family": "0" }
#
#   File we keep the history of uploaded images in.
#
HISTORY_FILE = "uploadr.history"

##
##  You shouldn't need to modify anything below here
##
FLICKR["secret" ] = "4273bf03b90b6adc"
FLICKR["api_key" ] = "04bb4d7119a20ca262a7b2c07c7e0f81"

class Uploadr:

    def __init__( self ):
        self.flickr = flickrapi.FlickrAPI(FLICKR["api_key"], FLICKR["secret"])
        (token, frob) = self.flickr.get_token_part_one(perms='write')
        if not token:
            raw_input("Press ENTER after you have authorised this program")
        self.flickr.get_token_part_two((token, frob))

    def upload( self ):
        newImages = self.grabNewImages()
        for image in newImages:
            self.uploaded = shelve.open( HISTORY_FILE )
            self.uploadImage( image )
            self.uploaded.close()

    def grabNewImages( self ):
        images = []
        foo = os.walk( IMAGE_DIR )
        for data in foo:
            (dirpath, dirnames, filenames) = data
            for f in filenames :
                ext = f.lower().split(".")[-1]
                if ( ext == "jpg" or
                     ext == "gif" or
                     ext == "png"):
                    images.append( os.path.normpath( dirpath + "/" + f ) )
        images.sort()
        return images

    def uploadImage( self, image ):
        if ( not self.uploaded.has_key( image ) ):
            print "Uploading ", image
            f = open(image, 'rb')
            metadata = exifread.process_file(f)
            try:
                date = time.strptime("%s" % metadata["Image DateTime"],
                        "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                print e
                date = time.localtime()

            response = self.flickr.upload(filename = image,
                               tags = FLICKR["tags"],
                               is_public = FLICKR["is_public"],
                               is_friend = FLICKR["is_friend"],
                               is_family = FLICKR["is_family"])

            if (response.attrib['stat'] == "ok"):
                pid = response.getchildren()[0].text
                try:
                    self.flickr.photos_setDates(photo_id = pid,
                        date_posted = "%d" % time.mktime(date))
                except flickrapi.exceptions.FlickrError:
                    print "Can't set date, pressing on anyway"
                self.logUpload(pid, image);

    def logUpload( self, photoID, imageName ):
        photoID = str( photoID )
        imageName = str( imageName )
        self.uploaded[ imageName ] = photoID
        self.uploaded[ photoID ] = imageName

if __name__ == "__main__":
    flick = Uploadr()
    flick.upload()
