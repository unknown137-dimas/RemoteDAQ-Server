import flet as ft

def main(page: ft.Page):
    page.title = 'RemoteDAQ Dashboard'
    theme = ft.Theme()
    theme.color_scheme_seed = 'green'
    theme.page_transitions.windows = ft.PageTransitionTheme.CUPERTINO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = theme
    
    nav = ['/', '/settings', '/about']

    '''Result Table'''
    result_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("First name")),
            ft.DataColumn(ft.Text("Last name")),
            ft.DataColumn(ft.Text("Age"), numeric=True),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("John")),
                    ft.DataCell(ft.Text("Smith")),
                    ft.DataCell(ft.Text("43")),
                ],
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Jack")),
                    ft.DataCell(ft.Text("Brown")),
                    ft.DataCell(ft.Text("19")),
                ],
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Alice")),
                    ft.DataCell(ft.Text("Wong")),
                    ft.DataCell(ft.Text("25")),
                ],
            ),
        ],
    )

    def checkbox_generator(n, obj):
        for i in range(n):
            obj.controls.append(ft.Checkbox(label='Pin ' + str(i)))

    '''IO Dropdown Function'''
    def io_dropdown_changed(_):
        print(io_dropdown.value)
        if io_dropdown.value == 'Input':
            input_tab.visible = True
            output_tab.visible = False
        if io_dropdown.value == 'Output':
            input_tab.visible = False
            output_tab.visible = True
        page.update()

    '''IO Dropdown'''
    io_dropdown = ft.Dropdown(
        hint_text='Input/Output',
        on_change=io_dropdown_changed,
        width=200,
        options=[
        ft.dropdown.Option('Input'),
        ft.dropdown.Option('Output'),
        ]
    )

    '''Columns'''
    analog_input_column = ft.Column(
        alignment = ft.MainAxisAlignment.SPACE_EVENLY
    )
    digital_input_column = ft.Column(
        alignment = ft.MainAxisAlignment.SPACE_EVENLY
    )
    digital_output_input_column = ft.Column(
        alignment = ft.MainAxisAlignment.SPACE_EVENLY
    )
    analog_output_column = ft.Column(
        alignment = ft.MainAxisAlignment.SPACE_EVENLY
    )
    digital_output_column = ft.Column(
        alignment = ft.MainAxisAlignment.SPACE_EVENLY
    )

    '''Input Tab'''
    input_tab = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text='Analog',
                content=ft.Card(
                    content=ft.Container(
                        content=analog_input_column,
                                # ft.FilledButton(text="Get Analog Input"),
                        alignment=ft.alignment.center,
                    ),
                    elevation=3
                ),
            ),
            ft.Tab(
                text='Digital',
                content=ft.Card(
                    content=ft.Container(
                        content=digital_input_column,
                                # ft.FilledButton(text="Get Analog Input"),
                        alignment=ft.alignment.center,
                    ),
                    elevation=3
                ),
            ),
            ft.Tab(
                text='Digital Output',
                content=ft.Card(
                    content=ft.Container(
                        content=digital_output_input_column,
                                # ft.FilledButton(text="Get Analog Input"),
                        alignment=ft.alignment.center,
                    ),
                    elevation=3
                ),
            ),
        ],
        expand=1,
    )

    '''Output Tab'''
    output_tab = ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text='Analog',
                content=ft.Card(
                    content=ft.Container(
                        content=analog_input_column,
                                # ft.FilledButton(text="Get Analog Input"),
                        alignment=ft.alignment.center,
                    ),
                    elevation=3
                ),
            ),
            ft.Tab(
                text='Digital',
                content=ft.Card(
                    content=ft.Container(
                        content=digital_output_column,
                                # ft.FilledButton(text="Get Analog Input"),
                        alignment=ft.alignment.center,
                    ),
                    elevation=3
                ),
            ),
        ],
        expand=1,
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
                        ft.Row(
                            [
                                ft.TextField(label='Network ID', hint_text='Network ID')
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ),
        ],
        expand=1,
    )


    '''Navigation Menu'''
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
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

    '''Page View Route'''
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
                                    io_dropdown,
                                    input_tab,
                                    output_tab,
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
                                settings_tab
                                # ft.Column([ ft.Text('HAI Settings!')], alignment=ft.MainAxisAlignment.START, expand=True),
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
                                ft.Column([ ft.Text('HAI About!')], alignment=ft.MainAxisAlignment.START, expand=True),
                            ],
                            expand=True,
                        ),
                    ],
                )
            )
        page.update()

    '''Remove Page View'''
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    checkbox_generator(8, analog_input_column)
    checkbox_generator(8, digital_input_column)
    checkbox_generator(8, digital_output_input_column)
    checkbox_generator(8, analog_output_column)
    checkbox_generator(8, digital_output_column)
    page.go(page.route)

ft.app(target=main, view=ft.WEB_BROWSER)