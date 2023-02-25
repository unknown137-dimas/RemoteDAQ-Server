import flet as ft
import aiohttp
import json
import asyncio
from os import getenv
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import paramiko
import scp
import remoteDAQ_Logger

'''Logger Config'''
my_logger = remoteDAQ_Logger.get_logger('RemoteDAQ_Server')

'''API Requests Function'''
async def api_request(url, payload={}, headers={}) -> dict:
    headers['Content-Type'] = 'application/json'
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            if payload:
                value = json.dumps(payload)
                async with session.post(url, data=value) as response:
                    return await response.json()
            else:
                async with session.get(url) as response:
                    return await response.json()
    except aiohttp.ClientConnectorError:
        my_logger.error('### Failed to Connect ###')
        return {'success':False, 'data':['Connection refused, check connection']}
    except aiohttp.ContentTypeError:
        my_logger.error('### Return Type Error ###')
        return {'success':False, 'data':['Invalid token or network ID, please check again']}
    except Exception as e:
        my_logger.error('### Unexpected Error Occured ###')
        my_logger.error(e)
        return {'success':False, 'data':['Unexpected error, Error message: ' + str(e)]}

'''SSH Function'''
def ssh_client(host, username, password, command='', file='', port=22):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, port, username, password, timeout=3)
    except Exception as e:
        my_logger.error('### Unexpected Error Occured ###')
        my_logger.error(e)
    if file:
        try:
            with scp.SCPClient(ssh.get_transport()) as scp_client:
                scp_client.put(file, 'RemoteDAQ/' + file)
        except Exception as e:
            my_logger.error('### Unexpected Error Occured ###')
            my_logger.error(e)
        return 'OK'
    elif command:
        stdin, stdout, stderr = ssh.exec_command(command)
        err_out = stderr.read().decode('utf-8')
        if err_out:
            with open('logs/node_setup.log', 'w') as node_log:
                node_log.write(err_out)
            return 'ERR'
        if stdout.read().decode('utf-8'):
            return 'OK'

'''Card Class'''
class card(ft.UserControl):
    def __init__(self, container_padding=15, card_elevation=5, obj=None, height=580, width=300):
        super().__init__()
        self.container_padding = container_padding
        self.card_elevation = card_elevation
        self.obj = obj
        self.height = height
        self.width = width
    
    def build(self):
        return ft.Card(    
            ft.Container(
                self.obj,
                padding=self.container_padding,
            ),
            elevation=self.card_elevation,
            col={'sm': 3, 'md': 4, 'xl': 3},
            height=self.height,
            width=self.width,
        )

'''Result Table Class'''
class result_table(ft.DataTable):
    def __init__(self, row_headers=0, col_headers=['Pin', 'Value']):
        self.col_headers = col_headers
        self.row_headers = row_headers
        super().__init__(
            border=ft.border.all(1, ft.colors.SECONDARY),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.SECONDARY),
            show_checkbox_column=True,
            columns=[
                ft.DataColumn(ft.Text(i)) for i in self.col_headers
            ],
            rows=[
                ft.DataRow(
                    [ft.DataCell(ft.Text('')) for _ in range(len(self.col_headers))],
                    on_select_changed=self.cell_selected,
                ) for _ in range(0, self.row_headers)
            ]
        )
        for i in range(0, self.row_headers):
            self.rows[i].cells[0].content.value = str(i)

    '''Result Table Checkbox Function'''
    def cell_selected(self, e):
        e.control.selected = not e.control.selected
        self.update()

'''UI'''
def main(page: ft.Page):
    '''Init'''
    theme = ft.Theme()
    theme.color_scheme_seed = 'green'
    theme.page_transitions.windows = ft.PageTransitionTheme.CUPERTINO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = theme
    page.title = 'RemoteDAQ Dashboard'
    nav = ['/', '/status', '/about']
    
    '''Load Variables'''
    load_dotenv()
    zt_id = str(getenv('ZT_ID'))
    zt_net_id = str(getenv('ZT_NET_ID'))
    zt_token = str(getenv('ZT_TOKEN'))

    '''Alert Dialog'''
    def dialog(text, content=None, actions=None):
        page.dialog = ft.AlertDialog(
            title=ft.Text(text),
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True

    '''Result Table Instance'''
    ai_result_table =  result_table(8)
    di_result_table = result_table(8)
    doi_result_table = result_table(8)
    node_result_table = result_table(col_headers=['ID', 'Name', 'IP Address', 'Authorized', 'Online'])

    '''Dropdown Instance'''
    node_dropdown = ft.Dropdown(
        label='RemoteDAQ Node',
    )

    '''Get Node List Function'''
    def get_node_list():
        result = []
        if zt_net_id and zt_token:
            url = 'https://api.zerotier.com/api/v1/network/' + zt_net_id + '/member'
            headers = {'Authorization' : 'Bearer ' + zt_token}
            try:
                result = asyncio.run(api_request(url, headers=headers))
            except TypeError:
                pass
            except Exception as e:
                my_logger.error('### Unexpected Error Occured ###')
                my_logger.error(e)
        return result
    
    '''Update Node Dropdown Function'''
    def update_node_dropdown():
        if page.route == '/':
            new_node_list = ['{} | {}'.format(r['name'], r['config']['ipAssignments'][0]) for r in get_node_list() if r['nodeId'] != zt_id and r['online'] and r['config']['ipAssignments']]
            node_dropdown.options.clear()
            for node in new_node_list:
                node_dropdown.options.append(ft.dropdown.Option(node))
            page.update()

    '''Update Node Status Table Function'''
    def update_status_table():
        if page.route == '/status':
            new_node_list = [r for r in get_node_list() if r['nodeId'] != zt_id]
            node_result_table.rows.clear()
            for n in new_node_list:
                node_ip = n['config']['ipAssignments'][0] if n['config']['ipAssignments'] else ''
                node_result_table.rows.append(
                    ft.DataRow(
                        [
                            ft.DataCell(ft.Text(n['nodeId'], selectable=True)),
                            ft.DataCell(ft.Text(n['name'], selectable=True)),
                            ft.DataCell(ft.Text(node_ip, selectable=True)),
                            ft.DataCell(ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN)) if n['config']['authorized'] else ft.DataCell(ft.Icon(ft.icons.ERROR, color=ft.colors.RED)),
                            ft.DataCell(ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN)) if n['online'] else ft.DataCell(ft.Icon(ft.icons.ERROR, color=ft.colors.RED)),
                        ]
                    )
                )
            node_result_table.update()

    '''Add Node Function'''
    def add_node(e):
        pb = ft.ProgressBar(width=250, visible=False)
        result_text = ft.Text('', weight=ft.FontWeight.BOLD)
        node_id = ft.TextField(label='Node ID')
        node_name = ft.TextField(label='Node Name')
        ssh_user = ft.TextField(label='SSH Username')
        ssh_pass = ft.TextField(label='SSH Password', password=True, can_reveal_password=True)

        def execute(e):
            result_text.value = 'Loading...'
            result_text.color = ft.colors.BLACK
            pb.visible = True
            apply_button.disabled = True
            zt_url = 'https://api.zerotier.com/api/v1/network/' + zt_net_id + '/member/' + str(node_id.value)
            headers = {'Authorization' : 'Bearer ' + zt_token}
            auth_result = asyncio.run(api_request(zt_url, payload={'name': node_name.value, 'config': {'authorized': True}}, headers=headers))
            if auth_result['config']['authorized']:
                ip_result = asyncio.run(api_request(zt_url, headers=headers))
                node_ip = ip_result['config']['ipAssignments'][0]
                scp_result = ssh_client(host=node_ip,
                            username=ssh_user.value,
                            password=ssh_pass.value,
                            file='.env-node'
                            )
                if scp_result:
                    ssh_result = ssh_client(host=node_ip,
                                username=ssh_user.value,
                                password=ssh_pass.value,
                                command='bash -c "cd RemoteDAQ; sudo ansible-playbook remotedaq_node_setup.yml"'
                                )
                    if ssh_result:
                        result_text.value = ssh_result
                        if ssh_result == 'ERR':
                            result_text.color = ft.colors.RED
                        pb.visible = False
                        apply_button.disabled = False
                
        apply_button = ft.FilledButton('Apply', on_click=execute)
        
        dialog('Configure a New Node',
            content=ft.Column(
                [
                    node_id,
                    node_name,
                    ssh_user,
                    ssh_pass,
                    pb,
                ],
                height=300
            ),
            actions=[result_text, apply_button]
        )
        page.update()

    '''Parse Data Function'''
    def parse_data(api_response, output_table):
        for row in output_table.rows:
            if row.selected:
                sel_pin = int(row.cells[0].content.value)
                pin = api_response['data'][sel_pin]
                row.cells[1].content.value = pin['value']
            else:
                row.cells[1].content.value = ''
        output_table.update()
        return 'Success'

    '''DAQ Function'''
    def daq(endpoint, result_table=None, daq_pin_values=None):
        selected_node = str(node_dropdown.value).split(' | ')[1] if node_dropdown.value else ''
        url = 'http://' + selected_node + ':8000' + endpoint
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
                result = asyncio.run(api_request(url, payload={'value': daq_pin_values}))
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
            e.control.color = ft.colors.RED
            e.control.error_text = 'Invalid value'
        else:
            e.control.color = ft.colors.PRIMARY
            e.control.error_text = ''
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
        helper_text='Valid range is 0 - 5 Volt',
        error_style=ft.TextStyle(color=ft.colors.RED)
        )
    ao_pin_1 = ft.TextField(
        label='AO Pin 1',
        suffix_text='Volt',
        on_change=check_ao_value,
        helper_text='Valid range is 0 - 5 Volt',
        error_style=ft.TextStyle(color=ft.colors.RED)
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

    '''Status Menu'''
    status_menu = card(obj=
        ft.Column(
            [
                ft.Text('Node Status', weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        node_result_table,
                    ],
                    scroll=ft.ScrollMode.ADAPTIVE,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=1,
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
        width=800
    )

    '''About Menu'''
    about_menu = card(obj=
        ft.Column(
            [
                ft.Text('Made with 💖 by Dimas Fitrio Kurniawan'),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=1,
            scroll=ft.ScrollMode.ADAPTIVE,
        )
    )

    '''AppBar Menu'''
    appbar = ft.AppBar(
        title=ft.Text("RemoteDAQ Dashboard"),
        center_title=True,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    '''Floating Action Button'''
    fab = ft.FloatingActionButton(
        icon=ft.icons.ADD,
        on_click=add_node
    )

    '''Navigation Menu'''
    rail = ft.NavigationRail(
        label_type=ft.NavigationRailLabelType.ALL,
        width=100,
        height=page.height,
        leading=ft.FloatingActionButton(icon=ft.icons.ADD,
                                        text='Add',
                                        on_click=add_node),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.HOME_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.HOME),
                label='Home'
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.MONITOR_HEART_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.MONITOR_HEART_SHARP),
                label='Node Status',
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.INFO_OUTLINE),
                selected_icon_content=ft.Icon(ft.icons.INFO),
                label='About',
            ),
        ],
        on_change=lambda e: page.go(nav[e.control.selected_index]),
    )

    '''Navigation Bar'''
    navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(
                icon_content=ft.Icon(ft.icons.HOME_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.HOME),
                label='Home'
            ),
            ft.NavigationDestination(
                icon_content=ft.Icon(ft.icons.MONITOR_HEART_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.MONITOR_HEART_SHARP),
                label='Node Status',
            ),
            ft.NavigationDestination(
                icon_content=ft.Icon(ft.icons.INFO_OUTLINE),
                selected_icon_content=ft.Icon(ft.icons.INFO),
                label='About',
            ),
        ],
        on_change=lambda e: page.go(nav[e.control.selected_index]),
    )

    '''App View'''
    view = ft.Column(
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    divider = ft.VerticalDivider()
    active_view = ft.Row(
        [rail, divider, view],
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True
    )

    '''Page View Route Function'''
    def route_change(route):
        route_data = route.data
        rail.selected_index = nav.index(route_data)
        navbar.selected_index = nav.index(route_data)
        view.controls.clear()
        if route_data == '/':
            '''/ Route'''
            view.controls.append(node_dropdown)
            view.controls.append(main_tab)
        if route_data == '/status':
            '''/status Route'''
            view.controls.append(status_menu)
        if route_data == '/about':
            '''/about Route'''
            view.controls.append(about_menu)
        page.update()
    
    '''Page Resize Function'''
    def page_resize(e):
        if page.width < 600:
            rail.visible = False
            divider.visible = False
            fab.visible = True
            navbar.visible = True
        else:
            rail.visible = True
            divider.visible = True
            fab.visible = False
            navbar.visible = False
        page.update()
    page_resize('')

    page.appbar = appbar
    page.floating_action_button = fab
    page.navigation_bar = navbar
    page.add(active_view)
    page.on_resize = page_resize
    page.on_route_change = route_change
    page.go(page.route)

    '''Loop Subroutine'''
    sched = BackgroundScheduler()
    sched.add_job(update_node_dropdown, 'interval', seconds=3)
    sched.add_job(update_status_table, 'interval', seconds=3)
    sched.start()

if __name__ == '__main__':
    ft.app(target=main, view=ft.WEB_BROWSER, port=2023)