from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex as C
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
import math

# Using Material Design Widgets
from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.dialog import MDDialog
from kivymd.textfields import MDTextField
from kivymd.date_picker import MDDatePicker
from kivymd.snackbar import Snackbar

# database
from supplier import *
from table_buttons import *

class SupplierTable(GridLayout):
    count = NumericProperty(0)
    d = ObjectProperty(None)
    data_object = Supplier()
    # pagination
    pages = list()
    page = list()
    page_no = 0
    current = 0
    offset = 11
    _data = None
    data_in_page = None

    def __init__(self, **kwargs):
        super(SupplierTable, self).__init__(**kwargs)
        self.pagination_next()
        self.call_load()

    def delete_data(self, id):
        try:
            self.data_object.id = id
            self.data_object.delete_supplier()
            self.pagination_next(self.current)
        except KeyError:
            print "Key Not Found"
        except e:
            Snackbar(text=str(e)).show()


    def call_load(self):
        Clock.schedule_once(self.load_data)

    def pagination_next(self, page=1):
        self.current = int(page)
        no_pages = int(math.ceil(float(self.data_object.count_supplier()) / float(self.offset)))
        if self.current <= no_pages:
            offset = (self.current - 1) * self.offset
            self.data_in_page = self.data_object.get_suppliers_page(offset, self.offset)
            self.pages = list(self.data_in_page)
            self._data = self.pages
            self.call_load()
        else:
            deactivate = False
        if self.current >= no_pages:
            deactivate = True
            self.current = no_pages
        else:
            deactivate = False
        return deactivate, str(self.current)

    def pagination_prev(self, page=1):
        self.current = int(page)
        if self.current > 0:
            offset = (self.current - 1) * self.offset
            self.data_in_page = self.data_object.get_suppliers_page(offset, self.offset)
            self.pages = list(self.data_in_page)
            self._data = self.pages
            self.call_load()
        else:
            deactivate = True
            self.current = 1
        if self.current == 1:
            deactivate = True
        else:
            deactivate = False
        return deactivate, str(self.current)

    def load_data(self, dt):
        self.clear_widgets()
        self.count = self.current * self.offset - self.offset + 1
        for key in self._data:
            id = str(self.data_in_page.get(key)['id'])
            name = str(self.data_in_page.get(key)['name'])
            address = str(self.data_in_page.get(key)['address'])
            contact = str(self.data_in_page.get(key)['contact'])

            if self.count % 2 == 1:
                self.d = DataWidget2(self.count,
                                     size_hint_y=None,
                                     height='40px')
            else:
                self.d = DataWidget(self.count,
                                    size_hint_y=None,
                                    height='40px')

            b = EditButton(self, id, text="edit")
            de = DeleteButton(self, self.d, id, text="delete")
            option = BoxLayout()

            option.add_widget(b)
            option.add_widget(de)

            self.d.add_widget(DataLabel(text=str(self.count)))
            self.d.add_widget(DataLabel(text=name))
            self.d.add_widget(DataLabel(text=address))
            self.d.add_widget(DataLabel(text=contact))
            self.d.add_widget(option)

            super(SupplierTable, self).add_widget(self.d)
            self.count += 1

    def save_edited_data(self, id, name, address, contact):
        self.data_object.id = id
        self.data_object.name = name
        self.data_object.address = address
        self.data_object.contact = contact
        self.data_object.update_supplier()
        self.dialog.dismiss()
        self.pagination_next()

    def edit_data(self, id):
        name = self.data_in_page.get(id)['name']
        address = str(self.data_in_page.get(id)['address'])
        contact = self.data_in_page.get(id)['contact']
        b = GridLayout(size_hint=(None, None),
                       height='200px',
                       width="400px",
                       cols=2
                       )
        name_wid = DialogTextInput(name)
        address_wid = DialogTextInput(address)
        contact_wid = DialogTextInput(contact)

        b.add_widget(MDLabel(id='Name',
                             text="Destination",
                             size_hint_x=None,
                             width="90px"
                             ))
        b.add_widget(name_wid)
        b.add_widget(MDLabel(
            text="Address",
            size_hint_x=None,
            width="90px"))
        b.add_widget(address_wid)
        b.add_widget(MDLabel(id='Contact',
                             text="Status",
                             size_hint_x=None,
                             width="90px"))
        b.add_widget(contact_wid)

        self.dialog = MDDialog(title="This is a test dialog",
                               content=b,
                               size_hint=(None, None),
                               height="500px",
                               width="500px",
                               auto_dismiss=False)
        self.dialog.add_action_button("Save",
                                      action=lambda *x: self.save_edited_data(id, name_wid.text, address_wid.text,
                                                                              contact_wid.text))
        self.dialog.add_action_button("Cancel",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()
        self.pagination_next()
        self.call_load()

    def add_data(self, name, address, contact):
        self.data_object.name = name
        self.data_object.address = address
        self.data_object.contact = contact
        if name != '' and address!= '' and contact != '':
            self.data_object.insert_supplier()
        else:
            Snackbar(text=" You Need To Fill All Fields ").show()
        self.pagination_next()
        self.call_load()