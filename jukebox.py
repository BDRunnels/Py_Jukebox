import sqlite3
import tkinter


class Scrollbox(tkinter.Listbox):

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)

    def grid(self, row, column, sticky="nsw", rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky="nse", rowspan=rowspan)
        self["yscrollcommand"] = self.scrollbar.set


class DataListBox(Scrollbox):

    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)

        self.linked_box = None
        self.link_field = None
        self.link_value = None

        self.cursor = connection.cursor()
        self.table = table
        self.field = field

        self.bind("<<ListboxSelect>>", self.on_select)

        self.sql_select = "SELECT " + self.field + ", _id" + " FROM " + self.table
        if sort_order:
            self.sql_sort = " ORDER BY " + ','.join(sort_order)
        else:
            self.sql_sort = " ORDER BY " + self.field

    def clear(self):
        self.delete(0, tkinter.END)

    def link(self, widget, link_field):
        self.linked_box = widget
        widget.link_field = link_field

    def requery(self, link_value=None):
        self.link_value = link_value    # store ID so we know the "master" record we're populating from
        if link_value and self.link_field:
            sql = self.sql_select + " WHERE " + self.link_field + "=?" + self.sql_sort
            print(sql)      # TODO DELETE THIS LINE
            self.cursor.execute(sql, (link_value,))
        else:
            print(self.sql_select + self.sql_sort)      # TODO DELETE THIS LINE
            self.cursor.execute(self.sql_select + self.sql_sort)

        #  clear the listbox contents before reloading
        self.clear()
        for value in self.cursor:
            self.insert(tkinter.END, value[0])

        if self.linked_box:
            self.linked_box.clear()

    def on_select(self, event):
        if not event.widget.curselection():
            return
        if self.linked_box:
            index = int(self.curselection()[0])
            value = self.get(index),

            # GET THE ID FROM DB ROW, ensure we have correct one,
            # by including link_value if appropriate
            if self.link_value:
                value = value[0], self.link_value
                print(f"value: {value}")    # TODO DELETE
                sql_where = " WHERE " + self.field + "=? AND " + self.link_field + "=?"
            else:
                sql_where = " WHERE " + self.field + "=?"

            link_id = self.cursor.execute(self.sql_select + sql_where, value).fetchone()[1]
            self.linked_box.requery(link_id)

            # artist_id = conn.execute("SELECT artists._id FROM artists WHERE artists.name=?", artist_name).fetchone()
                # OLD CODE, works with commented out line above
        # alist = []
        # for row in conn.execute("SELECT albums.name FROM albums WHERE
        #       albums.artist=? ORDER BY albums.name", artist_id):
        #       alist.append(row[0])
        # album_listVar.set(tuple(alist))
        # songs_listVar.set(("Choose an Album",))

    # HANDLED BY DATALISTBOX
# def get_songs(event):
#     if not event.widget.curselection():
#         return
#
#     lb = event.widget
#     index = int(lb.curselection()[0])
#     print(f"Index get_song {index}")
#     album_name = lb.get(index),
#
#     # get album id from DB row
#     album_id = conn.execute("SELECT albums._id FROM albums WHERE albums.name=?", album_name).fetchone()
#     alist = []
#     for x in conn.execute("SELECT songs.title FROM songs WHERE songs.album=? ORDER BY songs.track", album_id):
#         alist.append(x[0])
#     songs_listVar.set(tuple(alist))


if __name__ == '__main__':
    conn = sqlite3.connect("music.sqlite")

    mainWindow = tkinter.Tk()
    mainWindow.title("Music DB Browser")
    mainWindow.geometry("1024x768")

    # columns
    mainWindow.columnconfigure(0, weight=2)
    mainWindow.columnconfigure(1, weight=2)
    mainWindow.columnconfigure(2, weight=2)
    mainWindow.columnconfigure(3, weight=1)  # spacer column on right side

    # rows
    mainWindow.rowconfigure(0, weight=1)
    mainWindow.rowconfigure(1, weight=5)
    mainWindow.rowconfigure(2, weight=5)
    mainWindow.rowconfigure(3, weight=1)

    # labels
    tkinter.Label(mainWindow, text="Artists").grid(row=0, column=0)
    tkinter.Label(mainWindow, text="Albums").grid(row=0, column=1)
    tkinter.Label(mainWindow, text="Songs").grid(row=0, column=2)

    # artist list box
    artist_list = DataListBox(mainWindow, conn, "artists", "name")
    artist_list.grid(row=1, column=0, sticky="nsew", rowspan=2, padx=(30, 0))
    artist_list.config(border=2, relief="sunken")

    artist_list.requery()

    # albums list box
    album_listVar = tkinter.Variable(mainWindow)
    album_listVar.set(("Choose an Artist",))
    album_list = DataListBox(mainWindow, conn, "albums", "name", sort_order=("name",))
    # album_list.requery()
    album_list.grid(row=1, column=1, sticky="nsew", padx=(30, 0))
    album_list.config(border=2, relief="sunken")

    artist_list.link(album_list, "artist")

    # songs list box
    songs_listVar = tkinter.Variable(mainWindow)
    songs_listVar.set(("Choose an Album",))
    songs_list = DataListBox(mainWindow, conn, "songs", "title", sort_order=("track", "title"))
    # songs_list.requery()
    songs_list.grid(row=1, column=2, sticky="nsew", padx=(30, 0))
    songs_list.config(border=2, relief="sunken")

    album_list.link(songs_list, "album")

    # main loop
    mainWindow.mainloop()
    print("closing db connection")
    conn.close()
