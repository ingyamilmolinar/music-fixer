import requests
import urllib
import string
import re
import time
import sys
import signal
from mutagen.mp4 import MP4
from xml.etree import ElementTree
from unidecode import unidecode
import glob
from datetime import datetime
from difflib import SequenceMatcher
import discogs_client
from googlesearch import search


class RecordingXMLRoot:
    recordingCount = 0
    recordings = []

    def __init__(self, root):
        self.recordings = []
        for recording in root.iter(musicbrainz + 'recording'):
            RecordingXMLRoot.recordingCount += 1
            Recording.releaseCount = 0
            recording = Recording(recording)
            self.recordings.append(recording)


class ReleaseXMLRoot:
    releaseCount = 0
    releases = []

    def __init__(self, root):
        self.releases = []
        for release in root.iter(musicbrainz + 'release'):
            ReleaseXMLRoot.releaseCount += 1
            release = Release(release, 1, ReleaseXMLRoot.releaseCount)
            self.releases.append(release)

class ArtistXMLRoot:
    artistCount=0
    artists = []

    def __init__(self, root):
        self.artists = []
        for artist in root.iter(musicbrainz + 'artist'):
            ArtistXMLRoot.artistCount += 1
            artist = Artist(artist)
            self.artists.append(artist)

class Artist:
    aliasCount=0
    releaseCount=0
    releaseGroupsCount=0
    artistName= 'artistName Unknown'
    artistID= 'artistID Unknown'
    releaseGroups=[]
    aliases=[]
    releases=[]

    def __init__(self, artist):
        try:
            self.artistName = artist.find(musicbrainz + 'name').text
        except:
            self.artistName = 'artistName Unknown'
        try:
            self.artistID =  artist.get('id')
        except:
            self.artistID = 'artistID Unknown'
        self.aliases = []
        for alias in artist.iter(musicbrainz + 'alias'):
            Artist.aliasCount += 1
            alias = alias.text
            self.aliases.append(alias)
        self.releaseGroups = []
        for releaseGroup in artist.iter(musicbrainz + 'release-group'):
            Artist.releaseGroupsCount += 1
            releaseGroup = ReleaseGroup(releaseGroup)
            self.releaseGroups.append(releaseGroup)
        self.releases = []
        for release in artist.iter(musicbrainz + 'release'):
            Artist.releaseCount += 1
            release = Release(release, 1, Artist.releaseCount)
            self.releases.append(release)

class Recording:
    releaseCount = 0
    recordingTitle = 'recordingTitle Unknown'
    recordingArtist = 'recordingArtist Unknown'
    recordingArtistID = 'recordingArtistID Unknown'
    releases = []

    def __init__(self, recording):
        try:
            self.recordingTitle = recording.find(musicbrainz + 'title').text
        except:
            self.recordingTitle = 'recordingTitle Unknown'
        try:
            self.recordingArtist = unidecode(
                recording.find(musicbrainz + 'artist-credit').find(musicbrainz + 'name-credit').find(
                    musicbrainz + 'artist').find(musicbrainz + 'name').text)
        except:
            self.recordingArtist = 'recordingArtist Unknown'
        try:
            self.recordingArtistID = recording.find(musicbrainz + 'artist-credit').find(
                musicbrainz + 'name-credit').find(musicbrainz + 'artist').get('id')
        except:
            self.recordingArtistID = 'recordingArtistID Unknown'
        self.releases = []
        for release in recording.iter(musicbrainz + 'release'):
            Recording.releaseCount += 1
            release = Release(release, RecordingXMLRoot.recordingCount, Recording.releaseCount)
            self.releases.append(release)


class Release:
    recordingCount = 0
    releaseCount = 0
    trackCount = 0
    releaseTitle = 'releaseTitle Unknown'
    releaseID = 'releaseID Unknown'
    releaseGroup = None
    releaseType = 'releaseType Unknown'
    releaseStatus = 'releaseStatus Unknown'
    releaseArtist = 'releaseArtist Unknown'
    releaseArtistID = 'releaseArtistID Unknown'
    releaseDate = 'releaseDate Unknown'
    releaseCountry = 'releaseCountry Unknown'
    tracks = []

    def __init__(self, release, recordingCount, releaseCount):
        self.recordingCount = recordingCount
        self.releaseCount = releaseCount
        try:
            self.releaseID = release.get('id')
            if self.releaseID is None:
                self.releaseID = 'releaseID Unknown'
        except:
            self.releaseID = 'releaseID Unknown'
        try:
            self.releaseTitle = release.find(musicbrainz + 'title').text
        except:
            self.releaseTitle = 'releaseTitle Unknown'
        try:
            self.releaseStatus = release.find(musicbrainz + 'status').text
        except:
            self.releaseStatus = 'releaseStatus Unknown'
        try:
            self.releaseArtist = unidecode(
                release.find(musicbrainz + 'artist-credit').find(musicbrainz + 'name-credit').find(
                    musicbrainz + 'artist').find(
                    musicbrainz + 'name').text)
        except:
            self.releaseArtist = 'releaseArtist Unknown'
        try:
            self.releaseArtistID = release.find(musicbrainz + 'artist-credit').find(musicbrainz + 'name-credit').find(
                musicbrainz + 'artist').get('id')
        except:
            self.releaseArtistID = 'releaseArtistID Unknown'
        try:
            self.releaseGroup = ReleaseGroup(release.find(musicbrainz + 'release-group'))
        except:
            self.releaseGroup = None
        try:
            self.releaseDate = release.find(musicbrainz + 'date').text
        except:
            self.releaseDate = 'releaseDate Unknown'
        try:
            self.releaseCountry = release.find(musicbrainz + 'country').text
        except:
            self.releaseCountry = 'releaseCountry Unknown'
        self.tracks = []
        for track in release.iter(musicbrainz + 'track'):
            Release.trackCount += 1
            track = Track(track)
            self.tracks.append(track)


class ReleaseGroup:
    releaseGroupID = 'releaseGroupID Unknown'
    releaseGroupPrimaryType = 'releaseGroupPrimaryType Unknown'
    releaseGroupType = 'releaseGroupType Unknown'

    def __init__(self, group):
        try:
            self.releaseGroupType = group.get('type')
            if self.releaseGroupType is None:
                self.releaseGroupType = 'releaseGroupType Unknown'
        except:
            self.releaseGroupType = 'releaseGroupType Unknown'
        try:
            self.releaseGroupID = group.get('id')
            if self.releaseGroupID is None:
                self.releaseGroupID = 'releaseGroupID Unknown'
        except:
            self.releaseGroupID = 'releaseGroupID Unknown'
        try:
            self.releaseGroupPrimaryType = group.find(musicbrainz + 'primary-type').text
            if self.releaseGroupPrimaryType is None:
                self.releaseGroupPrimaryType = 'releaseGroupPrimaryType Unknown'
        except:
            self.releaseGroupPrimaryType = 'releaseGroupPrimaryType Unknown'


class Track:
    trackID = 'trackID Unknown'
    trackPosition = 'trackPosition Unknown'
    trackNumber = 'trackNumber Unknown'
    trackTitle = 'trackTitle Unknown'
    trackLength = 'trackLength Unknown'

    def __init__(self, track):
        try:
            self.trackID = track.get('id')
            if self.trackID is None:
                self.trackID = 'trackID Unknown'
        except:
            self.trackID = 'trackID Unknown'
        try:
            self.trackPosition = track.find(musicbrainz + 'position').text
        except:
            self.trackPosition = 'trackPosition Unknown'
        try:
            self.trackNumber = track.find(musicbrainz + 'number').text
        except:
            self.trackNumber = 'trackNumber Unknown'
        try:
            recording = track.find(musicbrainz + 'recording')
            self.trackTitle = recording.find(musicbrainz + 'title').text
        except:
            self.trackTitle = 'trackTitle Unknown'
        try:
            self.trackLength = track.find(musicbrainz + 'length').text
        except:
            self.trackLength = 'trackLength Unknown'

class SongInfo:
    releaseTitle=''
    releaseID=''
    releaseType=''
    releaseDate='9999'
    releaseCountry=''
    releaseArtist=''
    trackTitle=''
    trackID=''
    trackPosition=''
    trackNumber=''
    def __init__(self, songInfo=None, discogs=False):
        if songInfo is not None:
            if discogs:
                if len(songInfo) == 4:
                    self.releaseTitle = str(songInfo[0])
                    self.releaseID = str(songInfo[1])
                    self.releaseType = ''
                    self.releaseDate = 9999
                    self.releaseCountry = ''
                    self.releaseArtist = ''
                    self.trackTitle = str(songInfo[2])
                    self.trackID= ''
                    self.trackPosition = str(songInfo[3])
                    self.trackNumber = ''
                else:
                    self.releaseTitle = str(songInfo[0])
                    self.releaseID = str(songInfo[1])
                    self.releaseType = str(songInfo[2])
                    releaseDate = songInfo[3]
                    if releaseDate == 0:
                        releaseDate = 9999
                    self.releaseDate=str(releaseDate)
                    self.releaseCountry = str(songInfo[4])
                    releaseArtists=''
                    i=0
                    for artist in songInfo[5]:
                        i=i+1
                        releaseArtists=releaseArtists+re.sub('\(\s*\d+\s*\)\s*$', '', str(artist.name))+','
                    if i>0:
                        self.releaseArtist = releaseArtists[0:len(releaseArtists)-1]
                    else:
                        self.releaseArtist=''
                    self.releaseImages = str(songInfo[6])
                    self.trackTitle = str(songInfo[7])
                    self.trackID = ''
                    self.trackPosition = str(songInfo[8])
                    self.trackNumber = ''
            else:
                self.releaseTitle=songInfo[0]
                self.releaseID=songInfo[1]
                self.releaseType=songInfo[2]
                self.releaseDate=songInfo[3]
                self.releaseCountry=songInfo[4]
                self.releaseArtist=songInfo[5]
                self.trackTitle=songInfo[6]
                self.trackID=songInfo[7]
                self.trackPosition=songInfo[8]
                self.trackNumber=songInfo[9]
        else:
            self.releaseTitle = ''
            self.releaseID = ''
            self.releaseType = ''
            self.releaseDate = '9999'
            self.releaseCountry = ''
            self.releaseArtist = ''
            self.trackTitle = ''
            self.trackID = ''
            self.trackPosition = ''
            self.trackNumber = ''

def filterLibArtist(lib_artist):
    if lib_artist is None:
        return None
    lib_artist = str(lib_artist).lower()
    lib_artist = lib_artist.replace('&', 'and')
    lib_artist = unidecode(lib_artist)
    lib_artist = re.sub('\(\s*\d+\s*\)\s*$', '', lib_artist)
    lib_artist = lib_artist.translate(translator)
    lib_artist = re.sub('^\s*', '', lib_artist)
    lib_artist = re.sub('\s*$', '', lib_artist)
    lib_artist = re.sub('ft(\s|\.).*$', '', lib_artist)
    lib_artist = re.sub('feat(\s|\.).*$', '', lib_artist)
    if lib_artist == 'acdc':
        lib_artist = 'ac/dc'
    elif lib_artist == 'da':
        lib_artist = 'daft punk'
    elif lib_artist == 'rem':
        lib_artist = 'R.E.M.'
    return lib_artist

def filterDiscogsArtist(lib_artist):
    if lib_artist is None:
        return None
    lib_artist = re.sub('\(\s*\d+\s*\)\s*$', '', lib_artist)
    return lib_artist

def filterLibSong(lib_song):
    if lib_song is None:
        return None
    lib_song = str(lib_song).lower()
    lib_song = lib_song.replace('&', 'and')
    lib_song = unidecode(lib_song)
    lib_song = lib_song.translate(translator)
    lib_song = re.sub('^\s*', '', lib_song)
    lib_song = re.sub('\s*$', '', lib_song)
    lib_song = re.sub('ft(\s|\.).*$', '', lib_song)
    lib_song = re.sub('feat(\s|\.).*$', '', lib_song)
    return lib_song


def requestIsValid(urlRequest, f, s):
    timeout = 60
    while timeout > 0:
        try:
            response = s.get(urlRequest)
        except:
            response = None
        if response is not None:
            root=None
            if '.json' in urlRequest:
                try:
                    root = response.json()
                except Exception as e:
                    if 'exceeding the allowable rate limit' in str(
                            response.content) or 'web server is currently busy' in str(response.content):
                        time.sleep(1)
                        root = None
                    elif 'not well formed' in str(response.content) or 'The item you have requested has a problem' in str(response.content) or 'Page Not Found' in str(response.content):
                        return None
                    else:
                        return None
            else:
                try:
                    root = ElementTree.fromstring(response.content)
                except Exception as e:
                    if 'exceeding the allowable rate limit' in str(
                            response.content) or 'web server is currently busy' in str(response.content):
                        time.sleep(1)
                        root = None
                    elif 'not well formed' in str(response.content):
                        return None
                    else:
                        return None
            if root is not None:
                return root
        else:
            time.sleep(5)
            timeout = timeout - 5


def validateRelease(release, libArtist, f):
    if release.releaseStatus != 'Official' and release.releaseStatus != 'Promotion':
        return None
    if similarity(filterLibArtist(release.releaseArtist), libArtist) < 0.9 and not 'Unknown' in release.releaseArtist:
        return None

    releaseType = 'releaseType Unknown'
    if not 'Unknown' in release.releaseGroup.releaseGroupPrimaryType and not 'Unknown' in release.releaseGroup.releaseGroupType:
        releaseType = release.releaseGroup.releaseGroupType
    else:
        if 'Unknown' in release.releaseGroup.releaseGroupType and not 'Unknown' in release.releaseGroup.releaseGroupPrimaryType:
            releaseType = release.releaseGroup.releaseGroupPrimaryType
        else:
            if not 'Unknown' in release.releaseGroup.releaseGroupType and 'Unknown' in release.releaseGroup.releaseGroupPrimaryType:
                releaseType = release.releaseGroup.releaseGroupType
    release.releaseType = releaseType

    releaseDate = 'releaseDate Unknown'
    if 'Unknown' not in release.releaseDate:
        releaseDate = re.match("\d{4}", release.releaseDate)
        releaseDate = str(releaseDate.group(0))
        try:
            releaseDate = datetime.strptime(releaseDate, '%Y-%m-%d')
            invalidDate = False
        except:
            try:
                releaseDate = datetime.strptime(releaseDate, '%Y-%m')
                invalidDate = False
            except:
                try:
                    releaseDate = datetime.strptime(releaseDate, '%Y')
                    invalidDate = False
                except:
                    releaseDate = 'releaseDate Unknown'
                    invalidDate = True
        if not invalidDate:
            releaseDate = releaseDate.strftime('%Y')
    release.releaseDate = releaseDate
    return (release)


def analyzeRelease(release, artistSongs, libArtist, artistsNames, f):
    print('Analyzing release...\n')
    urlRequest = "http://musicbrainz.org/ws/2/release/" + release.releaseID + "?inc=recordings+release-groups"
    releaseRootXML = requestIsValid(urlRequest, f, s)
    if releaseRootXML:
        print(urlRequest + '\n')
        songsReleaseXML = ReleaseXMLRoot(releaseRootXML)
        currentRelease = [release.releaseTitle, release.releaseID, release.releaseType, release.releaseDate,
                          release.releaseCountry, release.releaseArtist]
        tracksInRelease = 0
        for track in songsReleaseXML.releases[0].tracks:
            trackTitle = filterLibSong(track.trackTitle)
            for libSong in artistSongs[libArtist]:
                if similarity(libSong, trackTitle) >= 0.9:
                    tracksInRelease = tracksInRelease + 1
                    currentTrack = [track.trackTitle, track.trackID, track.trackPosition, track.trackNumber]
                    songInfo=SongInfo(currentRelease + currentTrack)
                    if songInfo not in artistSongs[libArtist][libSong]:
                        print('Appending:' + unidecode(str(
                            currentRelease + currentTrack)) + ' to artistSongs[' + libArtist + '][' + trackTitle + ']\n')
                        artistSongs[libArtist][libSong].append(songInfo)
        if tracksInRelease > 0:
            if 'Unknown' not in release.releaseArtist:
                try:
                    artistsNames[libArtist].append(release.releaseArtist)
                except:
                    emptyList = []
                    artistsNames.update({libArtist: emptyList})
                    artistsNames[libArtist].append(release.releaseArtist)

def setTags(filename,audiofile,artist='',song='',album='',albumArtist='',composer='',year='',description='',genre='',lyrics='',comment='', trackNumber=0, diskNumber=0, tempo=[0]):
    if artist != '':
        audiofile.tags['\xa9ART'] = artist
    if song != '':
        audiofile.tags['\xa9nam'] = song
    if album != '':
        audiofile.tags['\xa9alb'] = album
    if albumArtist != '':
        audiofile.tags['aART'] = albumArtist
    if year != '':
        audiofile.tags['\xa9day'] = year
    if comment != '':
        audiofile.tags['\xa9cmt'] = comment
    if artist != '':
        audiofile.tags['soar'] = artist
    if albumArtist != '':
        audiofile.tags['soaa'] = albumArtist
    if album != '':
        audiofile.tags['soal'] = album
    if song != '':
        audiofile.tags['sonm'] = song
    if tempo != 0:
        audiofile.tags['tmpo'] = tempo
    audiofile.tags.save(filename)

def similarity(string1, string2):
    return SequenceMatcher(None, string1, string2).ratio()


def signal_handler(signal, frame):
    print('Forced exit!')
    sys.exit(0)

def validateFilename(value,deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value

signal.signal(signal.SIGINT, signal_handler)
translator = str.maketrans({key: None for key in string.punctuation})
musicbrainz = '{http://musicbrainz.org/ns/mmd-2.0#}'
apikey='hqTbuf1Zny'

s = requests.Session()

def main():
    filenameCounter = 0
    artistSongs = {}
    artistsNames = {}
    filenames={}
    music_path = sys.argv[1]
    d_client = discogs_client.Client('musicCorrectorOOP/0.0.2', user_token='TpOVGnsdTpMrkPVaRhUqXZXUrapnKmEXyQOKukJf')
    for filename in glob.iglob(music_path + "/**/*.m4a", recursive=True):
        filenameCounter += 1
        audiofile = MP4(filename)
        libArtist = filterLibArtist(audiofile.tags.get('\xa9ART', [None])[-1])
        libSong = filterLibArtist(audiofile.tags.get('\xa9nam', [None])[-1])
        comment = filterLibSong(audiofile.tags.get('\xa9cmt', [None])[-1])

        if libArtist is None or libSong is None or comment == 'corrected2' or comment == '9999' or comment == 'correctedmanually':
            continue

        try:
            filenames[libArtist] is None
        except:
            emptyDict = {}
            filenames.update({libArtist: emptyDict})
        try:
            filenames[libArtist][libSong] is None
        except:
            emptyList = []
            filenames[libArtist].update({libSong: emptyList})

        filenames[libArtist][libSong]=filename

        print(
            '-----------------------------------------------------------------------------------------------------')
        print(unidecode(filename) + '')
        print(libArtist + '\t\t' + libSong + '')

        try:
            artistSongs[libArtist] is None
        except:
            emptyDict = {}
            artistSongs.update({libArtist: emptyDict})
        try:
            artistSongs[libArtist][libSong] is None
        except:
            emptyList = []
            artistSongs[libArtist].update({libSong: emptyList})

    #f.close()
    for libArtist in artistSongs:
        f = open('./db/'+libArtist, 'w')

        for libSong in artistSongs[libArtist]:
            try:
                print("Searching for " + libArtist + " " + libSong + " release +album -single -live -compilaton site:discogs.com")
                release_urls = search(libArtist + " " + libSong + " release +album -single -live -compilation site:discogs.com", num=5, stop=5, pause=60)
                for url in release_urls:
                    print(url)
                    if re.search('/master/[0-9]+$', url) is None and re.search('/release/[0-9]+$', url) is None:
                        continue
                    release_id = re.search(r'[0-9]+$', url).group()
                    print(release_id)
                    if re.search('/master/', url):
                        release = d_client.master(release_id).main_release
                    else:
                        release = d_client.release(release_id)
                    try:
                        print(release.title)
                    except discogs_client.exceptions.HTTPError as httperr:
                        continue
                    filtered_artist = filterLibArtist(re.sub('\(\s*\d+\s*\)\s*$', '', str(release.artists[0].name)))
                    name_similarity = similarity(filtered_artist, libArtist)
                    print("similarity of " + filtered_artist + " and " + libArtist + ": " + str(name_similarity))
                    if name_similarity < 0.8 and not (libArtist in filtered_artist or filtered_artist in libArtist):
                        continue
                    currentRelease = [release.title, release.id, release.formats,
                                      release.year,
                                      release.country, release.artists, 'NULL']
                    tracksInRelease = 0
                    for track in release.tracklist:
                        trackTitle = filterLibSong(track.title)
                        for libSong in artistSongs[libArtist]:
                            print(track.title)
                            if similarity(libSong, trackTitle) >= 0.8:
                                tracksInRelease = tracksInRelease + 1
                                currentTrack = [track.title, track.position]
                                songInfo = SongInfo(currentRelease + currentTrack, discogs=True)
                                songInfoFound = False
                                for songinfo in artistSongs[libArtist][libSong]:
                                    if (songinfo.releaseTitle == songInfo.releaseTitle) and (
                                            songinfo.releaseDate == songInfo.releaseDate) and (
                                            songinfo.trackPosition == songInfo.trackPosition):
                                        songInfoFound = True
                                        break
                                if not songInfoFound:
                                    print('Appending:' + unidecode(str(
                                        currentRelease + currentTrack)) + ' to artistSongs[' + libArtist + '][' + libSong + ']')
                                    artistSongs[libArtist][libSong].append(songInfo)
                    if tracksInRelease > 0:
                        for artist in release.artists:
                            artistName = filterDiscogsArtist(artist.name)
                            try:
                                artistsNames[libArtist].append(artistName)
                            except:
                                emptyList = []
                                artistsNames.update({libArtist: emptyList})
                                artistsNames[libArtist].append(artistName)
                        print("artistsNames[" + libArtist + "]: " + artistName)
            except urllib.error.HTTPError as httperr:
                print(httperr.code)
                print(httperr.reason)
                print(httperr.headers)
                print(httperr.read())

        # Skip discogs
        if False:
            ####################### DISCOGS ##################################
            urlEncodedArtist = urllib.parse.quote_plus(libArtist)
            artists = d_client.search(libArtist, type='artist')
            artistCount=0
            for artist in artists:
                if artistCount>10:
                    break
                artistCount = artistCount+1
                name_similarity = similarity(filterLibArtist(artist.name), libArtist)
                print("similarity of "+filterLibArtist(artist.name)+" and "+libArtist+": "+str(name_similarity))
                if name_similarity >= 0.9:
                    try:
                        unidecode(str(artist.releases))
                    except:
                        continue
                    print(artist.name)
                    for release in artist.releases:
                        if release.__class__.__name__ == 'Master':
                            release = release.main_release
                        try:
                            formatsString=str(release.formats)
                        except:
                            formatsString=None

                        if formatsString is not None and (('Compilation' in formatsString) or (
                        'Transcription' in formatsString) or (
                        'Promo' in formatsString) or (
                        'Reissue' in formatsString) or (
                        'Unofficial Release' in formatsString) or (
                        'Partially Unofficial' in formatsString)):
                            continue

                        artistFound=False
                        for artist in release.artists:
                            if similarity(filterLibArtist(artist.name),libArtist) >= 0.9:
                                artistFound=True
                        if not artistFound:
                            continue
                        currentRelease = [release.title, release.id, release.formats,
                                          release.year,
                                          release.country, release.artists, 'NULL']
                        try:
                            unidecode(str(release.tracklist))
                        except:
                            continue
                        print("Release: " + str(release.title))
                        tracksInRelease=0
                        for track in release.tracklist:
                            trackTitle = filterLibSong(track.title)
                            for libSong in artistSongs[libArtist]:
                                if similarity(libSong, trackTitle) >= 0.9:
                                    tracksInRelease = tracksInRelease + 1
                                    currentTrack = [track.title, track.position]
                                    songInfo = SongInfo(currentRelease + currentTrack, discogs=True)
                                    songInfoFound = False
                                    for songinfo in artistSongs[libArtist][libSong]:
                                        if (songinfo.releaseTitle == songInfo.releaseTitle) and (
                                            songinfo.releaseDate == songInfo.releaseDate) and (
                                            songinfo.trackPosition == songInfo.trackPosition):
                                            songInfoFound=True
                                            break
                                    if not songInfoFound:
                                        print('Appending:' + unidecode(str(
                                            currentRelease + currentTrack)) + ' to artistSongs[' + libArtist + '][' + libSong + ']')
                                        artistSongs[libArtist][libSong].append(songInfo)
                        if tracksInRelease > 0:

                            for artist in release.artists:
                                artistName=filterDiscogsArtist(artist.name)
                                try:
                                    artistsNames[libArtist].append(artistName)
                                except:
                                    emptyList = []
                                    artistsNames.update({libArtist: emptyList})
                                    artistsNames[libArtist].append(artistName)
                            print("artistsNames["+libArtist+"]: "+artistName)
            ####################### DISCOGS ##################################

        # Skip musicbrainz
        if False:

            urlRequest = "http://musicbrainz.org/ws/2/artist/?query=artist:\"" + urlEncodedArtist + "\""
            artistRootXML = requestIsValid(urlRequest, f, s)

            if artistRootXML:
                artistXML = ArtistXMLRoot(artistRootXML)
                for artist in artistXML.artists:
                    if similarity(filterLibArtist(artist.artistName),libArtist) > 0.9:
                        try:
                            artistIDs[libArtist].append(artist.artistID)
                        except:
                            emptyList = []
                            artistIDs.update({libArtist: emptyList})
                            artistIDs[libArtist].append(artist.artistID)
                    else:
                        for alias in artist.aliases:
                            if similarity(filterLibArtist(alias),
                                          libArtist) > 0.9:
                                try:
                                    artistIDs[libArtist].append(artist.artistID)
                                except:
                                    emptyList = []
                                    artistIDs.update({libArtist: emptyList})
                                    artistIDs[libArtist].append(artist.artistID)

            try:
                artistIDs[libArtist] = list(set(artistIDs[libArtist]))
            except:
                artistIDs[libArtist] = list()
            for artistID in artistIDs[libArtist]:
                urlRequest = "http://musicbrainz.org/ws/2/artist/" + artistID + "?inc=releases+release-rels"
                artistRootXML = requestIsValid(urlRequest, f, s)
                if artistRootXML:
                    print(urlRequest + '')
                    artistXML = ArtistXMLRoot(artistRootXML)
                    for artistRelease in artistXML.artists[0].releases:
                        urlRequest = "http://musicbrainz.org/ws/2/release/" + artistRelease.releaseID + "?inc=release-groups+recordings"
                        releaseRootXML = requestIsValid(urlRequest, f, s)
                        if releaseRootXML:
                            print(urlRequest + '')
                            releaseXML = ReleaseXMLRoot(releaseRootXML)
                            for release in releaseXML.releases:
                                release = validateRelease(release, libArtist, f)
                                if release:
                                    if 'Unknown' not in release.releaseArtistID:
                                        try:
                                            artistIDs[libArtist].append(release.releaseArtistID)
                                        except:
                                            emptyList = []
                                            artistIDs.update({libArtist: emptyList})
                                            artistIDs[libArtist].append(release.releaseArtistID)
                                    analyzeRelease(release, artistSongs, libArtist, artistsNames, f)
        for libSong in artistSongs[libArtist]:
            oldestAlbum=SongInfo()
            oldestSingle=SongInfo()
            oldestEP=SongInfo()
            oldestSoundtrack=SongInfo()
            possibleAlbum=SongInfo()
            possibleSingle=SongInfo()
            possibleEP=SongInfo()
            possibleSoundtrack=SongInfo()
            selectedAlbum=SongInfo()
            for songInfo in artistSongs[libArtist][libSong]:
                if 'Unknown' not in songInfo.releaseDate and 'Unknown' not in songInfo.releaseType:
                    if ('Album' in songInfo.releaseType or 'LP' in songInfo.releaseType) and int(oldestAlbum.releaseDate) > int(songInfo.releaseDate):
                        oldestAlbum=songInfo
                    else:
                        if 'Single' in songInfo.releaseType and int(oldestSingle.releaseDate) > int(songInfo.releaseDate):
                            oldestSingle=songInfo
                        else:
                            if 'EP' in songInfo.releaseType and int(oldestEP.releaseDate) > int(songInfo.releaseDate):
                                oldestEP=songInfo
                            else:
                                if 'Soundtrack' in songInfo.releaseType and int(oldestSoundtrack.releaseDate) > int(
                                        songInfo.releaseDate):
                                    oldestSoundtrack = songInfo
                elif 'Unknown' not in songInfo.releaseType:
                    if 'Album' in songInfo.releaseType or 'LP' in songInfo.releaseType:
                        possibleAlbum=songInfo
                    elif 'Single' in songInfo.releaseType:
                        possibleSingle=songInfo
                    elif 'EP' in songInfo.releaseType:
                        possibleEP=songInfo
                    elif 'Soundtrack' in songInfo.releaseType:
                        possibleSoundtrack=songInfo
            if oldestAlbum.releaseTitle != '':
                selectedAlbum = oldestAlbum
            else:
                if oldestEP.releaseTitle != '':
                    selectedAlbum = oldestEP
                else:
                    if possibleAlbum.releaseTitle != '':
                        selectedAlbum = possibleAlbum
                    else:
                        if possibleEP.releaseTitle != '':
                            selectedAlbum = possibleEP
                        else:
                            if oldestSingle.releaseTitle != '':
                                selectedAlbum = oldestSingle
                            else:
                                if possibleSingle.releaseTitle != '':
                                    selectedAlbum = possibleSingle
                                else:
                                    if oldestSoundtrack.releaseTitle != '':
                                        selectedAlbum = oldestSoundtrack
                                    else:
                                        if possibleSoundtrack.releaseTitle != '':
                                            selectedAlbum = possibleSoundtrack

            print('+++++++++++Selected Album for '+ libSong +'++++++++++++++')
            print('|    D:' + unidecode(selectedAlbum.releaseTitle) + '')
            print('|      ' + selectedAlbum.releaseID + '')
            print('|    D:' + unidecode(selectedAlbum.releaseType) + '')
            print('|      ' + selectedAlbum.releaseDate + '')
            print('|      ' + selectedAlbum.releaseCountry + '')
            print('|    D:' + unidecode(selectedAlbum.releaseArtist) + '')
            print('|    D:' + unidecode(selectedAlbum.trackTitle) + '')
            print('|      ' + selectedAlbum.trackID + '')
            print('|      ' + selectedAlbum.trackPosition + '')
            print('|      ' + selectedAlbum.trackNumber + '')
            print('+++++++++++Selected Album for '+ libSong +'++++++++++++++')
            if str(selectedAlbum.releaseDate) != '9999':
                 audiofile=MP4(filenames[libArtist][libSong])
                 if 'Unknown' in selectedAlbum.releaseArtist:
                     selectedAlbum.releaseArtist=''
                 setTags(filenames[libArtist][libSong],audiofile,song=selectedAlbum.trackTitle,album=selectedAlbum.releaseTitle,albumArtist=selectedAlbum.releaseArtist,year=selectedAlbum.releaseDate,comment='corrected_2',tempo=[int(audiofile.info.bitrate/1000)])
            else:
                audiofile = MP4(filenames[libArtist][libSong])
                setTags(filenames[libArtist][libSong],audiofile, comment='9999', album='Unknown Album', tempo=[int(audiofile.info.bitrate/1000)])
        frequencyCounter=0
        mostFrequentArtist=''
        if libArtist in artistsNames:
            for artistName in artistsNames[libArtist]:
                if artistsNames[libArtist].count(artistName) > frequencyCounter:
                    frequencyCounter=artistsNames[libArtist].count(artistName)
                    mostFrequentArtist=artistName
            print('+++++++++++Selected artist Name :'+unidecode(mostFrequentArtist)+'')

        for libSong in artistSongs[libArtist]:
            audiofile=MP4(filenames[libArtist][libSong])
            setTags(filenames[libArtist][libSong],audiofile,artist=mostFrequentArtist)
        f.close()



if __name__ == "__main__":
    main()
    # Avoid 'Live' Albums
    # Reduce time by setting an algorithm where no further searching is required
    # Get song lyrics
    # Parallel processing on same machine (More accounts) Proxys?
