from .. import objects

class Builder:
    @classmethod
    def build_album(cls, album: objects.Album, traceback: set):
        print(album.option_string)
        if objects.Album in traceback:
            return
        traceback.add(objects.Album)
        
        for song in album.song_collection:
            song.album_collection.append(album)
    
    @classmethod
    def build_song(cls, song: objects.Song, traceback: set):
        print(song.option_string)
        if objects.Song in traceback:
            return
        traceback.add(objects.Song)
        
        for album in song.album_collection:
            album.song_collection.append(song)
            cls.build_album(album, traceback)
            
        for feature_artist in song.feature_artist_collection:
            feature_artist.feature_song_collection.append(song)
    
    @classmethod
    def build(cls, data_object: objects.MusicObject):
        if isinstance(data_object, objects.Song):
            cls.build_song(data_object, set())
            
        if isinstance(data_object, objects.Album):
            cls.build_album(data_object, set())
    