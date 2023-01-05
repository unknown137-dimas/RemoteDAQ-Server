import flet as ft
import aiohttp
import json
import asyncio
from os.path import exists

'''API Requests Function'''
async def api_request(url, payload=None, headers={}):
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

def main(page: ft.Page):
    '''Init'''
    theme = ft.Theme()
    theme.color_scheme_seed = 'green'
    theme.page_transitions.windows = ft.PageTransitionTheme.CUPERTINO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = theme
    page.title = 'RemoteDAQ Dashboard'
    
    nav = ['/', '/settings', '/about']
    card_elevation = 2
    container_padding = 15

    '''Alert Dialog'''
    def dialog(text):
        page.dialog = ft.AlertDialog(title=ft.Text(text))
        page.dialog.open = True

    '''Result Table'''
    ai_result_table = ft.DataTable(
        border=ft.border.all(3),
        vertical_lines=ft.border.BorderSide(1, 'black'),
        columns=[
            ft.DataColumn(ft.Text('Pin')),
            ft.DataColumn(ft.Text('Value'), numeric=True),
        ],
        rows=[
            ft.DataRow(
                [
                    ft.DataCell(ft.Text('0')),
                    ft.DataCell(ft.Text('')),
                ]
            ),
        ]
    )

    di_result_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('Pin')),
            ft.DataColumn(ft.Text('Value')),
        ],
    )
    doi_result_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('Pin')),
            ft.DataColumn(ft.Text('Value')),
        ],
    )

    '''Text Field'''
    zt_token = ft.TextField(label='ZeroTier Token')
    zt_net_id = ft.TextField(label='Network ID')

    '''Node Dropdown'''
    node_dropdown = ft.Dropdown(
        width=200,
    )
    '''Get Node List Function'''
    def get_node_list():
        print('Updating node list...')
        url = 'https://api.zerotier.com/api/v1/network/' + str(zt_net_id.value) + '/member'
        headers = {'Authorization' : 'Bearer ' + str(zt_token.value)}
        result = asyncio.run(api_request(url, headers=headers))
        return [r['config']['ipAssignments'][0] for r in result]

    '''Parse Data Function'''
    def parse_data(input, pins_list, output):
        output.rows.clear()
        for res in pins_list:
            row = input['data'][res]
            output.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row['port'])),
                        ft.DataCell(ft.Text(row['data']))
                    ]
                )
            )
        return 'Success'

    '''Load Settings Function'''
    def load_settings_file():
        if exists('settings.json'):
            with open('settings.json', 'r') as settings_file:
                if settings_file:
                    settings = json.loads(settings_file.readline())
                    zt_token.value = settings['zt_token']
                    zt_net_id.value = settings['zt_net_id']
    load_settings_file()

    '''Save Button Function'''
    def save_button_clicked(_):
        settings = {}
        settings['zt_token'] = zt_token.value
        settings['zt_net_id'] = zt_net_id.value
        with open('settings.json', 'w') as setings_file:
                setings_file.write(json.dumps(settings))

    '''AI Button Function'''
    def ai_button_clicked(_):
        selected_pins = [pin.data for pin in [
                ai_pin_0,
                ai_pin_1,
                ai_pin_2,
                ai_pin_3,
                ai_pin_4,
                ai_pin_5,
                ai_pin_6,
                ai_pin_7,
            ] if pin.value
        ]
        if selected_pins:
            print('Getting analog data for pin ' + str(selected_pins) + '...')
            url = 'http://localhost:8000/analog/input'
            result = asyncio.run(api_request(url))
            if result['success'] == True:
                output = parse_data(result, selected_pins, ai_result_table)
            else:
                output = result['data'][0]
        else:
            output = 'Please select one or more pin...'
        dialog(output)
        page.update()

    '''DI Button Function'''
    def di_button_clicked(_):
        selected_pins = [pin.data for pin in [
                di_pin_0,
                di_pin_1,
                di_pin_2,
                di_pin_3,
                di_pin_4,
                di_pin_5,
                di_pin_6,
                di_pin_7,
            ] if pin.value
        ]
        if selected_pins:
            print('Getting digital data for pin ' + str(selected_pins) + '...')
            url = 'http://localhost:8000/digital/input'
            result = asyncio.run(api_request(url))
            if result['success'] == True:
                output = parse_data(result, selected_pins, di_result_table)
            else:
                output = result['data'][0]
        else:
            output = 'Please select one or more pin...'
        dialog(output)
        page.update()

    '''DOI Button Function'''
    def doi_button_clicked(_):
        selected_pins = [pin.data for pin in [
                doi_pin_0,
                doi_pin_1,
                doi_pin_2,
                doi_pin_3,
                doi_pin_4,
                doi_pin_5,
                doi_pin_6,
                doi_pin_7,
            ] if pin.value
        ]
        if selected_pins:
            print('Getting digital output data for pin ' + str(selected_pins) + '...')
            url = 'http://localhost:8000/digital_output/input'
            result = asyncio.run(api_request(url))
            if result['success'] == True:
                output = parse_data(result, selected_pins, doi_result_table)
            else:
                output = result['data'][0]
        else:
            output = 'Please select one or more pin...'
        dialog(output)
        page.update()

    '''AO Button Function'''
    def ao_button_clicked(_):
        pin_values = [float(str(pin.value)) if pin.value != '' else 0 for pin in [
                ao_pin_0,
                ao_pin_1,
            ]
        ]
        print('Setting analog data...')
        url = 'http://localhost:8000/analog/output'
        result = asyncio.run(api_request(url, payload=pin_values))
        if result['success'] == True:
            output = 'Success'
        else:
            output = result['data'][0]
        dialog(output)
        page.update()
    
    '''DO Button Function'''
    def do_button_clicked(_):
        pin_values = [int(bool(pin.value)) for pin in [
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
        print('Setting digital data...')
        url = 'http://localhost:8000/digital/output'
        result = asyncio.run(api_request(url, payload=pin_values))
        if result['success'] == True:
            output = 'Success'
        else:
            output = result['data'][0]
        dialog(output)
        page.update()

    '''Check AO Value Function'''
    def check_ao_value(e):
        value = e.control.value
        if value and float(value) > 5:
            e.control.border_color = ft.colors.RED
            e.control.helper_text = 'Invalid value'
            e.control.prefix_icon = ft.icons.ERROR_OUTLINE
        else:
            e.control.border_color = ft.colors.PRIMARY
            e.control.helper_text = 'Valid range is 0 - 5 Volt'
            e.control.prefix_icon = ''
        page.update()

    '''Analog Input Pins'''
    ai_pin_0 = ft.Checkbox(label='AI Pin 0', data=0)
    ai_pin_1 = ft.Checkbox(label='AI Pin 1', data=1)
    ai_pin_2 = ft.Checkbox(label='AI Pin 2', data=2)
    ai_pin_3 = ft.Checkbox(label='AI Pin 3', data=3)
    ai_pin_4 = ft.Checkbox(label='AI Pin 4', data=4)
    ai_pin_5 = ft.Checkbox(label='AI Pin 5', data=5)
    ai_pin_6 = ft.Checkbox(label='AI Pin 6', data=6)
    ai_pin_7 = ft.Checkbox(label='AI Pin 7', data=7)
    
    '''Digital Input Pins'''
    di_pin_0 = ft.Checkbox(label='DI Pin 0', data=0)
    di_pin_1 = ft.Checkbox(label='DI Pin 1', data=1)
    di_pin_2 = ft.Checkbox(label='DI Pin 2', data=2)
    di_pin_3 = ft.Checkbox(label='DI Pin 3', data=3)
    di_pin_4 = ft.Checkbox(label='DI Pin 4', data=4)
    di_pin_5 = ft.Checkbox(label='DI Pin 5', data=5)
    di_pin_6 = ft.Checkbox(label='DI Pin 6', data=6)
    di_pin_7 = ft.Checkbox(label='DI Pin 7', data=7)
    
    '''Digital Output Input Pins'''
    doi_pin_0 = ft.Checkbox(label='DO Pin 0', data=0)
    doi_pin_1 = ft.Checkbox(label='DO Pin 1', data=1)
    doi_pin_2 = ft.Checkbox(label='DO Pin 2', data=2)
    doi_pin_3 = ft.Checkbox(label='DO Pin 3', data=3)
    doi_pin_4 = ft.Checkbox(label='DO Pin 4', data=4)
    doi_pin_5 = ft.Checkbox(label='DO Pin 5', data=5)
    doi_pin_6 = ft.Checkbox(label='DO Pin 6', data=6)
    doi_pin_7 = ft.Checkbox(label='DO Pin 7', data=7)
    
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
    
    '''Digital Output Pins'''
    do_pin_0 = ft.Switch(label='DO Pin 0', data=1)
    do_pin_1 = ft.Switch(label='DO Pin 1', data=1)
    do_pin_2 = ft.Switch(label='DO Pin 2', data=1)
    do_pin_3 = ft.Switch(label='DO Pin 3', data=1)
    do_pin_4 = ft.Switch(label='DO Pin 4', data=1)
    do_pin_5 = ft.Switch(label='DO Pin 5', data=1)
    do_pin_6 = ft.Switch(label='DO Pin 6', data=1)
    do_pin_7 = ft.Switch(label='DO Pin 7', data=1)

    for node in get_node_list():
        node_dropdown.options.append(ft.dropdown.Option(node))

    '''Input Row'''
    input_row = ft.ResponsiveRow(
        [
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text('Analog Input', weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ai_pin_0,
                                            ai_pin_1,
                                            ai_pin_2,
                                            ai_pin_3,
                                            ai_pin_4,
                                            ai_pin_5,
                                            ai_pin_6,
                                            ai_pin_7,
                                        ]
                                    ),
                                    ft.VerticalDivider(),
                                    ft.Column(
                                        [
                                            ai_result_table,
                                            ft.ElevatedButton(
                                                text='Get Analog Data',
                                                on_click=ai_button_clicked,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.colors.SECONDARY_CONTAINER
                                                )
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=container_padding,
                ),
                elevation=card_elevation,
                col={'md': 4},
            ),
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text('Digital Input', weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            di_pin_0,
                                            di_pin_1,
                                            di_pin_2,
                                            di_pin_3,
                                            di_pin_4,
                                            di_pin_5,
                                            di_pin_6,
                                            di_pin_7,
                                        ]
                                    ),
                                    ft.VerticalDivider(),
                                    ft.Column(
                                        [
                                            di_result_table,
                                            ft.ElevatedButton(
                                                text='Get Digital Data',
                                                on_click=di_button_clicked,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.colors.SECONDARY_CONTAINER
                                                )
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=container_padding,
                ),
                elevation=card_elevation,
                col={'md': 4},
            ),
            ft.Card(
                ft.Container(
                        ft.Column(
                            [
                                ft.Text('"Digital Output" Input', weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                doi_pin_0,
                                                doi_pin_1,
                                                doi_pin_2,
                                                doi_pin_3,
                                                doi_pin_4,
                                                doi_pin_5,
                                                doi_pin_6,
                                                doi_pin_7,
                                            ]
                                        ),
                                        ft.VerticalDivider(),
                                        ft.Column(
                                            [
                                                doi_result_table,
                                                ft.ElevatedButton(
                                                    text='Get Digital Output Data',
                                                    on_click=doi_button_clicked,
                                                    style=ft.ButtonStyle(
                                                        bgcolor=ft.colors.SECONDARY_CONTAINER
                                                    )
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=container_padding,
                ),
                elevation=card_elevation,
                col={'md': 4},
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    '''Output Row'''
    output_row = ft.ResponsiveRow(
        [
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text('Analog Output', weight=ft.FontWeight.BOLD),
                            ao_pin_0,
                            ao_pin_1,
                            ft.ElevatedButton(
                                text='Set Analog Data',
                                on_click=ao_button_clicked,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.SECONDARY_CONTAINER
                                )
                            ),
                        ],
                        # alignment=ft.MainAxisAlignment.CENTER,
                        # horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=container_padding,
                ),
                elevation=card_elevation,
                col={'md': 4},
            ),
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text('Digital Output', weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            do_pin_0,
                                            do_pin_1,
                                            do_pin_2,
                                            do_pin_3,
                                            do_pin_4,
                                            do_pin_5,
                                            do_pin_6,
                                            do_pin_7,
                                        ]
                                    ),
                                    ft.VerticalDivider(),
                                    ft.Column(
                                        [
                                            # do_result_table,
                                            ft.ElevatedButton(
                                                text='Set Digital Data',
                                                on_click=do_button_clicked,
                                                style=ft.ButtonStyle(
                                                    bgcolor=ft.colors.SECONDARY_CONTAINER
                                                )
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=container_padding,
                ),
                elevation=card_elevation,
                col={'md': 4},
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    '''Settings Tab'''
    settings_tab = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text='General',
                icon=ft.icons.SETTINGS,
                content=ft.Container(
                    content=ft.Text('This is Tab 1'), alignment=ft.alignment.center
                ),
            ),
            ft.Tab(
                text='Network',
                icon=ft.icons.CABLE,
                content=ft.Column(
                    [
                        ft.Container(
                            ft.Column(
                                [
                                    zt_token,
                                    zt_net_id,
                                ],
                            ),
                            padding=container_padding,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ),
        ],
        expand=1,
    )

    '''Navigation Menu'''
    rail = ft.NavigationRail(
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        min_width=100,
        min_extended_width=400,
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
        page.views.clear()
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
                                    input_row,
                                    output_row
                                ],
                                expand=True
                            ),
                        ],
                        expand=True,
                    ),
                ],
            )
        )
        if page.route == '/settings':
            '''/settings Route'''
            page.views.append(
                ft.View(
                    '/settings',
                    [
                        ft.Row(
                            [
                                rail,
                                ft.VerticalDivider(width=1),
                                settings_tab,
                                ft.ElevatedButton(
                                    'Save',
                                    on_click=save_button_clicked
                                )
                            ],
                            expand=True,
                        ),
                    ],
                )
            )
        if page.route == '/about':
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

if __name__ == '__main__':
    ft.app(target=main, view=ft.WEB_BROWSER, port=2023)