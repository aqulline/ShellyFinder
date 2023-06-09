import threading

from kivy.base import EventLoop
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy_garden.mapview import MapMarker, MapMarkerPopup
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from plyer import gps

from stations import GoogleStations as GS
from distance import Distance as DS
from locations import Location as LC
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy import utils

Window.keyboard_anim_args = {"d": .2, "t": "linear"}
Window.softinput_mode = "below_target"
Clock.max_iteration = 250

if utils.platform != 'android':
    Window.size = (412, 732)


class RowCard(MDCard):
    icon = StringProperty("")
    name = StringProperty("")


class MapButton(MDRaisedButton):
    cord = ListProperty([])


class MainApp(MDApp):
    size_x, size_y = Window.size
    thread = None
    zoom = NumericProperty(10)

    # Stations
    fuel_station = StringProperty("")
    cord_station = StringProperty("")
    f_station = ListProperty([])
    c_station = ListProperty([])

    # Locations
    address = StringProperty("")
    time = StringProperty("")
    distance = StringProperty("")

    # screen
    screens = ['home']
    screens_size = NumericProperty(len(screens) - 1)
    current = StringProperty(screens[len(screens) - 1])

    lat, lon = NumericProperty(-6.8059668), NumericProperty(39.2243981)

    def on_start(self):
        Clock.schedule_once(self.station, .2)
        self.keyboard_hooker()
        self.request_android_permissions()

    def get_location(self, *args):
        gps.configure(on_location=self.on_location_update)
        gps.start()

    def on_location_update(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.lon = float(lon)
        self.lat = float(lat)
        print(f"Latitude: {lat}, Longitude: {lon}")
        toast(f"Latitude: {lat}, Longitude: {lon}")
        gps.stop()

    def fetch_location(self):
        cordinates = [self.lat, self.lon]

        self.address = LC.get_address(LC(), cordinates)["display_name"]

    def fetch_address(self, cordinates):
        address = LC.get_address(LC(), cordinates)["display_name"]

        return address

    def station(self, *args):
        self.fetch_location()
        GS.GetBusStop(GS(), self.address)

    def add_item(self):
        names = GS.name_stop
        cor = GS.cord_stop
        for i in names:
            pos = names.index(i)
            self.root.ids.customers.data.append(
                {
                    "viewclass": "RowCard",
                    "icon": "google-maps",
                    "name": i,
                    "id": cor[pos]
                }
            )

    def add_recent(self):
        names = self.f_station
        cor = self.c_station
        for i in names:
            pos = names.index(i)
            self.root.ids.booking_list.data.append(
                {
                    "viewclass": "RowCard",
                    "icon": "google-maps",
                    "name": i,
                    "id": cor[pos]
                }
            )

    @mainthread
    def get_loc_time(self, cord):
        cordinates = [self.lat, self.lon]
        addres1 = self.fetch_address(cord)
        addres2 = self.fetch_address(cordinates)
        data = DS.get_distance(DS(), addres2, addres1)
        self.time, self.distance = str(data[1]), str(data[0])

    def bus_stop_specific(self, data, name):
        map = self.root.ids.map
        lat, lon = data.strip().split(",")
        mark = MapMarkerPopup(lat=lat, lon=lon, source="components/icons/station.png")
        mark.add_widget(MapButton(text=name, cord=[lat, lon]))
        map.add_widget(mark)
        map.center_on(float(lat), float(lon))

    """
            SCREENS FUNCTIONS
    """

    def keyboard_hooker(self, *args):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        print(self.screens_size)
        if key == 27 and self.screens_size > 0:
            print(f"your were in {self.current}")
            last_screens = self.current
            self.screens.remove(last_screens)
            print(self.screens)
            self.screens_size = len(self.screens) - 1
            self.current = self.screens[len(self.screens) - 1]
            self.screen_capture(self.current)
            return True
        elif key == 27 and self.screens_size == 0:
            toast('Press Home button!')
            return True

    def call(self):
        from call import Actions as AC

        AC.call(AC(), "0715700411")

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION, Permission.CALL_PHONE], callback)

    def screen_capture(self, screen):
        sm = self.root
        sm.current = screen
        if screen in self.screens:
            pass
        else:
            self.screens.append(screen)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        print(f'size {self.screens_size}')
        print(f'current screen {screen}')

    def screen_leave(self):
        print(f"your were in {self.current}")
        last_screens = self.current
        self.screens.remove(last_screens)
        print(self.screens)
        self.screens_size = len(self.screens) - 1
        self.current = self.screens[len(self.screens) - 1]
        self.screen_capture(self.current)

    def build(self):
        pass


MainApp().run()
