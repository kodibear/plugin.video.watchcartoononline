
#
#      Copyright (C) 2013 Sean Poyser
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import re
import urllib
import net
import base64

import wco_utils as utils

def decodeChar(char, charOffset):
    return chr(int(re.sub(r'\D', '', base64.b64decode(char))) - charOffset)

def Resolve(html):
    try:    
        results = []

        # get around the new URL encoding mechanism
        charOffset = re.search('String.fromCharCode.+? - ([\d]+?)\);', html).group(1)
        encodedString = re.search('<script>.+?var .+? = \[(.+?)\]', html).group(1)
        encodedChars = re.compile('\"(.+?=)\"').findall(encodedString)
        iframe = ''.join([ decodeChar(x, int(charOffset)) for x in encodedChars ])
        
        urls = re.compile('<iframe id.+?src="(.+?)".+?</iframe>').findall(iframe)

        for url in urls:
            if 'cizgifilmlerizle' in url:
                DoResolve(url, results)

            if 'animeuploads' in url:
                DoResolve(url, results)

            if 'vid44.php' in url:
                url = re.compile('iframe src=\"(.+)\" frameborder').search(html).group(1)
                html = utils.GetHTML(url)
                url = re.compile('file: \"(.+)\",\\r  height').search(html).group(1)
                results.append([url, text])

    except:
        pass

    if len(results) == 0:
        results = [[None, 'Error Resolving URL']]

    return results


def DoResolve(url, results):
    try:        
        theNet = net.Net()
        url  = utils.URL + url.replace(' ', '%20')[1:]

        theNet.set_user_agent(utils.getUserAgent())

        html  = theNet.http_GET(url).content.replace('\n', '').replace('\t', '')
        sources = re.compile('{(.+?)}').findall(re.compile('sources:\s*(\[.*?\])').findall(html, re.DOTALL)[0])
        
        for source in sources:
            try:
                fileUrl = re.compile('file:\s*?"(.+?)"').search(source).group(1)
                label = re.compile('label:\s*?"(.+?)"').search(source)
                if label:
                    label = label.group(1)
                else:
                    label = ''
                results.append([fileUrl, label])
            except:
                pass
 
        if len(results) == 0:
            links = re.compile(';file=(.+?)&provider=http\'').findall(html)
            for link in links:
                results.append([urllib.unquote_plus(link), ''])

    except:
        pass

    return results