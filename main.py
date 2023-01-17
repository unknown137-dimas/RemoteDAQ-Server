import flet as ft
import aiohttp
import json
import asyncio
from os.path import exists
from os import getenv
from apscheduler.schedulers.background import BackgroundScheduler

'''API Requests Function'''
async def api_request(url, payload=None, headers={}) -> dict:
    headers['Content-Type'] = 'application/json'
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            if payload:
                data = json.dumps({'data' : payload})
                async with session.put(url, data=data) as response:
                    return await response.json()
            else:
                async with session.get(url) as response:
                    return await response.json()
    except aiohttp.ClientConnectorError:
        return {'success':False, 'data':['Connection refused, check connection']}
    except aiohttp.ContentTypeError:
        return {'success':False, 'data':['Invalid token or network ID, please check again']}

'''Card Class'''
class card(ft.UserControl):
    def __init__(self, container_padding=15, card_elevation=5, obj=None):
        super().__init__()
        self.container_padding = container_padding
        self.card_elevation = card_elevation
        self.obj = obj
    
    def build(self):
        return ft.Card(    
            ft.Container(
                self.obj,
                padding=self.container_padding,
            ),
            elevation=self.card_elevation,
            col={'sm': 3, 'md': 4, 'xl': 3},
            height=580,
            width=300,
        )

'''Result Table Class'''
class result_table(ft.DataTable):
    def __init__(self, pin_count):
        self.pin_count = pin_count
        super().__init__(
            border=ft.border.all(1, ft.colors.SECONDARY),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.SECONDARY),
            show_checkbox_column=True,
            columns=[
                ft.DataColumn(ft.Text('Pin')),
                ft.DataColumn(ft.Text('Value'), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    [ft.DataCell(ft.Text(str(i))), ft.DataCell(ft.Text(''))],
                    on_select_changed=self.cell_selected,
                ) for i in range(0, self.pin_count)
            ]
        )

    '''Result Table Checkbox Function'''
    def cell_selected(self, e):
        e.control.selected = not e.control.selected
        self.update()

'''UI'''
def main(page: ft.Page):
    '''Init'''
    theme = ft.Theme()
    theme.color_scheme_seed = 'green'
    theme.page_transitions.windows = ft.PageTransitionTheme.NONE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = theme
    page.title = 'RemoteDAQ Dashboard'
    nav = ['/', '/settings', '/about']

    '''Alert Dialog'''
    def dialog(text):
        page.dialog = ft.AlertDialog(title=ft.Text(text))
        page.dialog.open = True

    '''Result Table Instance'''
    ai_result_table =  result_table(8)
    di_result_table = result_table(8)
    doi_result_table = result_table(8)

    '''Text Field Instance'''
    zt_token = ft.TextField(label='ZeroTier Token')
    zt_net_id = ft.TextField(label='Network ID')

    '''Node Dropdown'''
    node_dropdown = ft.Dropdown(
        label='RemoteDAQ Node',
        width=200,
    )

    '''Get Node List Function'''
    def get_node_list():
        url = 'https://api.zerotier.com/api/v1/network/' + str(zt_net_id.value) + '/member'
        headers = {'Authorization' : 'Bearer ' + str(zt_token.value)}
        try:
            result = asyncio.run(api_request(url, headers=headers))
            result = [r['config']['ipAssignments'][0] for r in result if r['nodeId'] != getenv('ZT_ID') and r['online']]
        except TypeError:
            result = []
        return result
    
    '''Update Node Dropdown Function'''
    def update_node_dropdown():
        if exists('settings.json'):
            new_node_list = get_node_list()
            node_dropdown_options = [opt.key for opt in node_dropdown.options]
            if node_dropdown_options != new_node_list:
                node_dropdown.options.clear()
                for node in new_node_list:
                    node_dropdown.options.append(ft.dropdown.Option(node))
                    page.update()

    '''Parse Data Function'''
    def parse_data(api_response, output_table):
        for row in output_table.rows:
            if row.selected:
                sel_pin = int(row.cells[0].content.value)
                pin = api_response['data'][sel_pin]
                row.cells[1].content.value = pin['data']
            else:
                row.cells[1].content.value = ''
        output_table.update()
        return 'Success'

    '''Save Settings Function'''
    def save_settings_file():
        settings = {}
        settings['zt_token'] = zt_token.value
        settings['zt_net_id'] = zt_net_id.value
        with open('settings.json', 'w') as setings_file:
                setings_file.write(json.dumps(settings))

    '''Load Settings Function'''
    def load_settings_file():
        if exists('settings.json'):
            with open('settings.json', 'r') as settings_file:
                if settings_file:
                    settings = json.loads(settings_file.readline())
                    zt_token.value = settings['zt_token']
                    zt_net_id.value = settings['zt_net_id']
        else:
            save_settings_file()
    load_settings_file()

    '''Save Button Function'''
    def save_button_clicked(_):
        save_settings_file()
        dialog('Settings saved succesfully')
        page.update()

    '''DAQ Function'''
    def daq(endpoint, result_table=None, daq_pin_values=None):
        selected_node = node_dropdown.value
        url = 'http://' + str(selected_node) + ':8000' + endpoint
        if selected_node:
            if result_table:
                daq_pins = [row.cells[0].content.value for row in result_table.rows if row.selected]
                if daq_pins:
                    result = asyncio.run(api_request(url))
                    if result['success'] == True:
                        dialog(parse_data(result, result_table))
                    else:
                        dialog(result['data'][0])
                else:
                    dialog('Please select one or more pin...')
            if daq_pin_values:
                result = asyncio.run(api_request(url, payload=daq_pin_values))
                if result['success'] == True:
                    dialog('Success')
                else:
                    dialog(result['data'][0])
        else:
            dialog('Please select destination remoteDAQ node...')
        page.update()

    '''DAQ Selected Pins'''
    def output_pins(e):
        out_type = e.control.text.lower().split(' ')[1:-1][0]
        if out_type == 'analog':
            return [float(str(pin.value)) if pin.value != '' else 0 for pin in [
                    ao_pin_0,
                    ao_pin_1,
                ]
            ]
        
        if out_type == 'digital':
            return [int(bool(pin.value)) for pin in [
                    do_pin_0,
                    do_pin_1,
                    do_pin_2,
                    do_pin_3,
                    do_pin_4,
                    do_pin_5,
                    do_pin_6,
                    do_pin_7,
                ]
            ]

    '''Check AO Value Function'''
    def check_ao_value(e):
        value = e.control.value
        if value and float(value) > 5:
            e.control.border_color = ft.colors.RED
            e.control.helper_text = 'Invalid value'
        else:
            e.control.border_color = ft.colors.PRIMARY
            e.control.helper_text = 'Valid range is 0 - 5 Volt'
        e.control.update()

    '''Reset All AO Pins Function'''
    def ao_pins_reset_clicked(e):
        ao_pin_0.value = '0'
        ao_pin_0.update()
        ao_pin_1.value = '0'
        ao_pin_1.update()

    '''Analog Output Pins'''
    ao_pin_0 = ft.TextField(
        label='AO Pin 0',
        suffix_text='Volt',
        on_change=check_ao_value,
        helper_text='Valid range is 0 - 5 Volt'
        )
    ao_pin_1 = ft.TextField(
        label='AO Pin 1',
        suffix_text='Volt',
        on_change=check_ao_value,
        helper_text='Valid range is 0 - 5 Volt'
        )
    
    '''Toggle All DO Pins Function'''
    def do_pins_all_clicked(e):
        value = do_pin_0.value
        value = not value
        do_pin_0.value = value
        do_pin_0.update()
        do_pin_1.value = value
        do_pin_1.update()
        do_pin_2.value = value
        do_pin_2.update()
        do_pin_3.value = value
        do_pin_3.update()
        do_pin_4.value = value
        do_pin_4.update()
        do_pin_5.value = value
        do_pin_5.update()
        do_pin_6.value = value
        do_pin_6.update()
        do_pin_7.value = value
        do_pin_7.update()
        

    '''Digital Output Pins'''
    do_pin_0 = ft.Switch(label='DO Pin 0')
    do_pin_1 = ft.Switch(label='DO Pin 1')
    do_pin_2 = ft.Switch(label='DO Pin 2')
    do_pin_3 = ft.Switch(label='DO Pin 3')
    do_pin_4 = ft.Switch(label='DO Pin 4')
    do_pin_5 = ft.Switch(label='DO Pin 5')
    do_pin_6 = ft.Switch(label='DO Pin 6')
    do_pin_7 = ft.Switch(label='DO Pin 7')

    '''API Endpoints'''
    ai_endpoint = '/analog/input'
    di_endpoint = '/digital/input'
    doi_endpoint = '/digital_output/input'
    ao_endpoint = '/analog/output'
    do_endpoint = '/digital/output'

    '''Input Row'''
    input_row = ft.Row(
        [
            card(obj=
                ft.Column(
                    [
                        ft.Container(
                            expand=1,
                            content=ft.Text('Analog Input', weight=ft.FontWeight.BOLD)
                        ),
                        ft.Container(
                            expand=11,
                            content=ai_result_table
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.FilledButton(
                                'Get Analog Data',
                                on_click=lambda e: daq(ai_endpoint, result_table=ai_result_table),
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
            card(obj=
                ft.Column(
                    [
                        ft.Container(
                            expand=1,
                            content=ft.Text('Digital Input', weight=ft.FontWeight.BOLD)
                        ),
                        ft.Container(
                            expand=11,
                            content=di_result_table
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.FilledButton(
                                'Get Digital Data',
                                on_click=lambda e: daq(di_endpoint, result_table=di_result_table),
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
            card(obj=
                ft.Column(
                    [
                        ft.Container(
                            expand=1,
                            content=ft.Text('"Digital Output" Input', weight=ft.FontWeight.BOLD)
                        ),
                        ft.Container(
                            expand=11,
                            content=doi_result_table
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.FilledButton(
                                'Get Digital Output Data',
                                on_click=lambda e: daq(doi_endpoint, result_table=doi_result_table),
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        scroll=ft.ScrollMode.ADAPTIVE,
        wrap=True,
    )

    '''Output Row'''
    output_row = ft.Row(
        [
            card(obj=
                ft.Column(
                    [
                        ft.Container(
                            expand=1,
                            content=ft.Text('Analog Output', weight=ft.FontWeight.BOLD)
                        ),
                        ft.Container(
                            expand=11,
                            content=ft.Column(
                                [
                                    ao_pin_0,
                                    ao_pin_1
                                ]
                            )
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.Row(
                                [
                                    ft.FilledButton(
                                        'Set Analog Data',
                                        on_click=lambda e: daq(ao_endpoint, daq_pin_values=output_pins(e)),
                                    ),
                                    ft.ElevatedButton(
                                        'Reset All Pins',
                                        on_click=ao_pins_reset_clicked,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.colors.SECONDARY_CONTAINER
                                        )
                                    ),
                                ]
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
            card(obj=
                ft.Column(
                    [
                        ft.Container(
                            expand=1,
                            content=ft.Text('Digital Output', weight=ft.FontWeight.BOLD)
                        ),
                        ft.Container(
                            expand=11,
                            content=ft.Column(
                                [
                                    do_pin_0,
                                    do_pin_1,
                                    do_pin_2,
                                    do_pin_3,
                                    do_pin_4,
                                    do_pin_5,
                                    do_pin_6,
                                    do_pin_7
                                ]
                            )
                        ),
                        ft.Container(
                            expand=1,
                            content=ft.Row(
                                [
                                    ft.FilledButton(
                                        'Set Digital Data',
                                        on_click=lambda e: daq(do_endpoint, daq_pin_values=output_pins(e)),
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.colors.SECONDARY_CONTAINER,
                                        )
                                    ),
                                    ft.ElevatedButton(
                                        'Toggle All Pins',
                                        on_click=do_pins_all_clicked,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.colors.SECONDARY_CONTAINER
                                        )
                                    ),
                                ]
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        scroll=ft.ScrollMode.ADAPTIVE,
        wrap=True,
    )

    '''Main Tab'''
    main_tab = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text='Input',
                content=ft.Container(
                    input_row
                ),
            ),
            ft.Tab(
                text='Output',
                content=ft.Container(
                    output_row
                ),
            ),
        ],
        expand=1,
    )

    '''Settings Tab'''
    # settings_tab = ft.Tabs(
    #     selected_index=0,
    #     animation_duration=300,
    #     tabs=[
    #         ft.Tab(
    #             text='General',
    #             icon=ft.icons.SETTINGS,
    #             content=ft.Container(
    #                 content=result_table(10), alignment=ft.alignment.center
    #             ),
    #         ),
    #         ft.Tab(
    #             text='Network',
    #             icon=ft.icons.CABLE,
    #             content=ft.Column(
    #                 [
    #                     ft.Container(
    #                         ft.Column(
    #                             [
    #                                 zt_token,
    #                                 zt_net_id,
    #                             ],
    #                         ),
    #                         padding=container_padding,
    #                     )
    #                 ],
    #                 alignment=ft.MainAxisAlignment.START,
    #             ),
    #         ),
    #     ],
    #     expand=1,
    # )

    settings_menu = ft.Row(
        [
            card(obj=
                ft.Column(
                    [
                        zt_net_id,
                        zt_token,
                        ft.FilledButton(
                            'Save',
                            on_click=save_button_clicked
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ),
            
        ],
        wrap=True
    )

    # '''AppBar Menu'''
    # appbar = ft.AppBar(
    #     leading=ft.IconButton(ft.icons.HOME, on_click=lambda e: page.go('/')),
    #     leading_width=40,
    #     title=ft.Text("RemoteDAQ Dashboard"),
    #     center_title=False,
    #     bgcolor=ft.colors.SURFACE_VARIANT,
    #     elevation=card_elevation,
    #     actions=[
    #         # ft.IconButton(ft.icons.HOME),
    #         ft.IconButton(ft.icons.SETTINGS, on_click=lambda e: page.go('/settings')),
    #     ],
    # )

    # '''Floating Action Button'''
    # fab = ft.FloatingActionButton(
    #     icon=ft.icons.ADD
    # )

    '''Navigation Menu'''
    rail = ft.NavigationRail(
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        min_width=100,
        leading=ft.FloatingActionButton(icon=ft.icons.ADD, text='Add'),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label='Home'
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text('Settings'),
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.INFO_OUTLINE),
                selected_icon_content=ft.Icon(ft.icons.INFO),
                label='About',
            ),
        ],
        on_change=lambda e: page.go(nav[e.control.selected_index]),
    )    

    '''Page View Route Function'''
    def route_change(route):
        route_data = route.data
        rail.selected_index = nav.index(route_data)
        page.views.clear()
        if route_data == '/':
            '''/ Route'''
            page.views.append(
                ft.View(
                    '/',
                    [
                        ft.Row(
                            [
                                rail,
                                ft.VerticalDivider(width=1),
                                ft.Column(
                                    [
                                        node_dropdown,
                                        main_tab,
                                    ],
                                    expand=True
                                ),
                            ],
                            expand=True,
                        ),
                    ],
                )
            )
        if route_data == '/settings':
            '''/settings Route'''
            page.views.append(
                ft.View(
                    '/settings',
                    [
                        ft.Row(
                            [
                                rail,
                                ft.VerticalDivider(width=1),
                                ft.Column(
                                    [
                                        settings_menu
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    expand=True
                                )
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            expand=True,
                        ),
                    ],
                )
            )
        if route_data == '/about':
            '''/about Route'''
            page.views.append(
                ft.View(
                    '/about',
                    [
                        ft.Row(
                            [
                                rail,
                                ft.VerticalDivider(width=1),
                                ft.Column([ ft.Text('Made with 💖 by Dimas Fitrio Kurniawan')], alignment=ft.MainAxisAlignment.START, expand=True),
                            ],
                            expand=True,
                        ),
                    ],
                )
            )
        page.update()

    '''Remove Page View Function'''
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    '''Loop Subroutine'''
    sched = BackgroundScheduler()
    sched.add_job(update_node_dropdown, 'interval', seconds=3)
    sched.start()

if __name__ == '__main__':
    ft.app(target=main, view=ft.WEB_BROWSER, port=2023)