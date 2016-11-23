# -*- coding: cp1250 -*-

# general
from __future__ import division
from dnBaseLib import *
# import PIL
#
# import subprocess

# python modules
# import os
# import ttk
# import types
# import copy
# solsec modules
# import ssConstants

# design modules
import dnConstants
import dnComponent
import dnComponentDlg
import numpy

import collections

# soldis
# import sdConstants
import sdRTFReport
# import sdSchemeImageMaker

#soldis env
# import soSymbols

#add
# import PyRTF

#CONSTANTS
from soWidgets import *

final_capacity_ratio = 'Final Capacity Ratio'


def n_calc(num):
    linspace = numpy.linspace(-1, 1, num).tolist()
    return linspace


def calc_bound(numb_f, a1_spac, alfa0, numb_f_r, a2_spac, alfa1):
    # calculate farthest connector in a principal column
    rtop_ele0 = (numb_f - 1) / 2 * a1_spac
    xtop_ele0 = sin(alfa0) * rtop_ele0
    ytop_ele0 = cos(alfa0) * rtop_ele0
    column1 = n_calc(numb_f)
    coords_col1 = []
    # calculate other connectors in a principal column,
    # having their positions ratio from n_calc multiplied by farthest connector
    for coord in column1:
        coords_col1.append([coord * xtop_ele0, coord * ytop_ele0])

    # calculate farthest connector in a principal row
    rtop_ele1 = (numb_f_r - 1) / 2 * a2_spac
    xtop_ele1 = sin(alfa1) * rtop_ele1
    ytop_ele1 = cos(alfa1) * rtop_ele1
    row1 = n_calc(numb_f_r)
    coords_row1 = []
    # calculate other connectors in a principal row,
    # having their positions ratio from n_calc multiplied by farthest connector
    for coord in row1:
        coords_row1.append([coord * xtop_ele1, coord * ytop_ele1])

    # add principal column coordinates to each principal row coordinate, thus obtaining every connector coordinate
    coords_unred = []
    for i in range(len(coords_row1)):
        coords_unred.append(numpy.add(coords_row1[i], coords_col1).tolist())

    #reduce coords nested lists amount
    coord_redux = []
    for i in range(len(coords_unred)):
        for p in coords_unred[i]:
            coord_redux.append(p)

    # extract x and y coordinates
    xcoords = []
    ycoords = []
    for p in coord_redux:
        xcoords.append(p[0])
        ycoords.append(p[1])

    return xcoords, ycoords


def calc_connectors_with_displacement(numb_f, a1_spac, alfa0, numb_f_r, a2_spac, alfa1, displacement, plate_l):
    delta_x = sin(alfa0) * displacement
    delta_y = cos(alfa0) * displacement

    plate_l_x = sin(alfa0) * plate_l / 2
    plate_l_y = cos(alfa0) * plate_l / 2

    if abs(alfa0 - alfa1) < radians(20):
        alfa1 = alfa0 - pi / 2
    if abs(abs(alfa0 - alfa1) - pi) < radians(20):
        alfa1 = alfa0 - pi / 2

    # calculate farthest connector in a principal column
    rtop_ele0 = (numb_f - 1) / 2 * a1_spac
    xtop_ele0 = sin(alfa0) * rtop_ele0
    ytop_ele0 = cos(alfa0) * rtop_ele0

    column1 = n_calc(numb_f)
    coords_col1 = []
    # calculate other connectors in a principal column,
    # having their positions ratio from n_calc multiplied by farthest connector
    for coord in column1:
        coords_col1.append([coord * xtop_ele0, coord * ytop_ele0])

    # calculate farthest connector in a principal row
    rtop_ele1 = (numb_f_r - 1) / 2 * a2_spac
    xtop_ele1 = sin(alfa1) * rtop_ele1
    ytop_ele1 = cos(alfa1) * rtop_ele1
    row1 = n_calc(numb_f_r)
    coords_row1 = []
    # calculate other connectors in a principal row,
    # having their positions ratio from n_calc multiplied by farthest connector
    for coord in row1:
        coords_row1.append([coord * xtop_ele1, coord * ytop_ele1])

    # add principal column coordinates to each principal row coordinate, thus obtaining every connector coordinate
    coords_unred = []
    for i in range(len(coords_row1)):
        coords_unred.append(numpy.add(coords_row1[i], coords_col1).tolist())

    #reduce coords nested lists amount
    coord_redux = []
    for i in range(len(coords_unred)):
        for p in coords_unred[i]:
            coord_redux.append(p)

    # apply displacement
    for coord in coord_redux:
        coord[0] += delta_x + plate_l_x
        coord[1] += delta_y + plate_l_y

    # extract x and y coordinates
    xcoords = []
    ycoords = []
    for p in coord_redux:
        xcoords.append(p[0])
        ycoords.append(p[1])

    # calculate radiuses and their square sum
    rad = [sqrt(pq[0] ** 2 + pq[1] ** 2) for pq in coord_redux]
    rad_squared = [rq ** 2 for rq in rad]
    rad_sum = sum(rad_squared)

    return coord_redux, xcoords, ycoords, rad, rad_sum


class PolaczenieDrewnianeDlg(dnComponentDlg.ComponentContextNodeDlg):
    SHOW_MANAGER = False
    controlWidth = 12

    def __init__(self, parent, comp_obj, **kw):

        #wywolanie klasy bazowej
        dnComponentDlg.ComponentContextNodeDlg.__init__(self, parent, comp_obj, **kw)

        # self.registerLoadCombTab()

        self.registerTab('1',
                         text='Design connection',
                         createFunc=self.create_tab1,
                         updateFun=self.update_tab1,
                         subjectId=0)
        self.registerTab('2',
                         text='Info',
                         createFunc=self.create_info,
                         updateFun=self.update_info)

        #ustawienie zakladki domyslnej
        self.setDefaultTab('1')

        self.registerPermamentPanel(
            createFun=self.create_panel,
            updateFun=self.update_panel)

        self.registerRaportGeneratorButton()

        self.build()

    def setVars(self):

        # checks and radios
        # self.addVar('forces_ignore_sign', type='IntVar')
        self.addVar('forces_chb', type='IntVar')
        self.addVar('connect_to_radio', type='IntVar')
        self.addVar('nail_radio', type='StringVar')
        self.addVar('calc_bend_tens', type='IntVar')
        self.addVar('two_sided', type='IntVar')
        self.addVar('predrilled_holes', type='IntVar')

        self.addVar('designed_id_str', type='StringVar')
        self.addVar('other_id_str', type='StringVar')

        self.addVar('k_mod', type='DoubleVar')
        self.addVar('gamma_m', type='DoubleVar')
        self.addVar('calc_axially_loaded', type='IntVar')
        self.addVar('f_ax_ed', type='DoubleVar')

        self.addVar('diameter', type='DoubleVar')
        self.addVar('num_of_fasteners', type='IntVar')
        self.addVar('num_of_rows', type='IntVar')
        self.addVar('a1', type='DoubleVar')
        self.addVar('a2', type='DoubleVar')
        self.addVar('nail_length', type='IntVar')

        self.addVar('theta', type='IntVar')
        self.addVar('f_u', type='IntVar')

        self.addVar('bolt_str', type='StringVar')
        self.addVar('boltd_str', type='StringVar')
        self.addVar('l_control', type='DoubleVar')

        self.addVar('axial_f', type='DoubleVar')
        self.addVar('shear_f', type='DoubleVar')
        self.addVar('bending_m', type='DoubleVar')

        self.addVar('force_plate_inside', type='IntVar')
        self.addVar('plate_l', type='IntVar')
        self.addVar('plate_h', type='IntVar')
        self.addVar('plate_t', type='IntVar')
        self.addVar('plate_delta', type='IntVar')

    def create_panel(self, tab):

        frame = soFrame(tab)
        frame.pack()

        canvas_frame = soFrame(frame)
        canvas_frame.grid(row=1, column=1)

        self.canvas = soMetricCanvas(canvas_frame, width=265, height=270, bg='white', relief='flat', bd=1)
        self.canvas.pack(fill=BOTH)

        # notebook
        notebook = soNoteBook(frame)
        notebook.grid(row=2, column=1, sticky=S + W + N + E, padx=1, pady=1)

        designed_bars = soFrame(notebook)
        connection_pref_tab = soFrame(notebook)
        notebook.add(designed_bars, image=self._createImage('geometry_icon'))
        notebook.add(connection_pref_tab, image=self._createImage('connect_pref'))

        # ! designed_bars
        designed_label = soLabel(designed_bars, text='General settings')
        designed_label.pack()
        separator = soSeparator(designed_bars, orient='horizontal')
        separator.pack(fill=X, pady=3)

        designed_right_and_left = soFrame(designed_bars)
        designed_right_and_left.pack(expand=1, fill=BOTH)

        # designed_bars_left
        designed_bars_left = soFrame(designed_right_and_left)
        designed_bars_left.pack(side=LEFT, fill=BOTH)

        node_object = self.getCompObj().getItem()
        results = self.getCompObj().getResults()
        self.bars_li = []

        designed_id_label = soLabel(designed_bars_left, text='Designed bar ID')
        designed_id_label.pack(side=TOP, padx=3, pady=1)

        self.designed_id_combo = soComboBox(designed_bars_left,
                                            state='readonly',
                                            width=10,
                                            values=self.bars_li,
                                            textvariable=self.var_designed_id_str)
        self.designed_id_combo.pack(side=TOP, padx=3, pady=1)

        soLabel(designed_bars_left, text='Design connection\nwith: ',
                justify='center').pack(side=TOP, anchor=W, padx=3, pady=1)

        connect_to_radio1 = soRadiobutton(designed_bars_left,
                                          text="Other bar",
                                          value=0,
                                          variable=self.var_connect_to_radio)
        connect_to_radio1.pack(side=TOP, padx=3, pady=1)

        connect_to_radio2 = soRadiobutton(designed_bars_left,
                                          text="Steel plate",
                                          value=1,
                                          variable=self.var_connect_to_radio)
        connect_to_radio2.pack(side=TOP, padx=3, pady=1)

        separator = soSeparator(designed_right_and_left, orient='vertical')
        separator.pack(side=LEFT, fill=Y, pady=3)

        # designed_bars_right switchframe

        designed_bars_right = soFrame(designed_right_and_left)
        designed_bars_right.pack(side=LEFT, expand=1, fill=BOTH)

        self.designed_bars_switchframe = dnComponentDlg.SwitchFrame(designed_bars_right)
        self.designed_bars_switchframe.pack()

        connection_with_other_bar = soFrame(self.designed_bars_switchframe)
        connection_with_other_bar.pack()
        self.designed_bars_switchframe.add(connection_with_other_bar)

        connection_with_steel_plate = soFrame(self.designed_bars_switchframe)
        connection_with_steel_plate.pack()
        self.designed_bars_switchframe.add(connection_with_steel_plate)

        self.designed_bars_switchframe.switch(0)

        # connection with other bar

        soLabel(connection_with_other_bar, text='ID of the bar bearing\nthe connection',
                justify='center').pack(side=TOP, padx=3, pady=1)

        self.other_id_combo = soComboBox(connection_with_other_bar,
                                         state='readonly',
                                         width=10,
                                         values=self.bars_li,
                                         textvariable=self.var_other_id_str)
        self.other_id_combo.pack(side=TOP, padx=3, pady=1)

        def validate_0(x):
            try:
                x = float(x)
            except TypeError:
                return 1
            if x < 0.1:
                x = 0.1
            return x

        self.l_control_hiddenframe = dnComponentDlg.HiddenFrame(connection_with_other_bar)
        self.l_control_hiddenframe.pack(side=TOP, padx=3, pady=3)
        l_control_frame = soFrame(self.l_control_hiddenframe)
        self.l_control_hiddenframe.insert(l_control_frame)

        separator = soSeparator(l_control_frame, orient='horizontal')
        separator.pack(fill=X, pady=3)

        soLabel(l_control_frame, text='Flat connection\noverlap length:',
                justify='center').pack(side=TOP, padx=3, pady=1)
        l_control = soControl(l_control_frame,
                              variable=self.var_l_control,
                              image=self._createImage('image085'),
                              step=1,
                              width=5,
                              allowempty=False,
                              validatecmd=validate_0,
                              selectmode='normal',
                              round=2)
        l_control.pack(padx=3, pady=1)

        # connection with steel plate

        soLabel(connection_with_steel_plate, text='Steel plate settings', justify='center').pack(side=TOP, padx=3,
                                                                                                 pady=1)

        soSeparator(connection_with_steel_plate, orient='horizontal').pack(fill=X, pady=3)

        force_plate_inside_chb = soCheckbutton(connection_with_steel_plate,
                                               text=u"Steel plate inside\nhole drilled in profile",
                                               variable=self.var_force_plate_inside)
        force_plate_inside_chb.pack(side=TOP, padx=3, pady=1)

        plate_l_control = soControl(connection_with_steel_plate,
                                    variable=self.var_plate_l,
                                    image=self._createImage('image081'),
                                    step=1,
                                    width=5,
                                    allowempty=False,
                                    validatecmd=validate_0,
                                    selectmode='normal',
                                    round=2)
        plate_l_control.pack(side=TOP, padx=3, pady=1)

        plate_h_control = soControl(connection_with_steel_plate,
                                    variable=self.var_plate_h,
                                    image=self._createImage('image082'),
                                    step=1,
                                    width=5,
                                    allowempty=False,
                                    validatecmd=validate_0,
                                    selectmode='normal',
                                    round=2)
        plate_h_control.pack(side=TOP, padx=3, pady=1)

        # switch plate_t_control to label when steel plate is inside
        self.plate_t_switch_frame = dnComponentDlg.SwitchFrame(connection_with_steel_plate)
        self.plate_t_switch_frame.pack(side=TOP, padx=3, pady=1)

        self.plate_t_control_frame = soFrame(self.plate_t_switch_frame)
        self.plate_t_control_frame.pack()
        self.plate_t_switch_frame.add(self.plate_t_control_frame)

        self.plate_t_label_frame = soFrame(self.plate_t_switch_frame)
        self.plate_t_label_frame.pack()
        self.plate_t_switch_frame.add(self.plate_t_label_frame)

        plate_t_control = soControl(self.plate_t_control_frame,
                                    variable=self.var_plate_t,
                                    image=self._createImage('image083'),
                                    step=1,
                                    width=5,
                                    allowempty=False,
                                    validatecmd=validate_0,
                                    selectmode='normal',
                                    round=2)
        plate_t_control.pack()

        self.plate_t_val = dnComponentDlg.ResultValue(self.plate_t_label_frame, format='%.f',
                                                      lImage=self._createImage('image083'))
        self.plate_t_val.pack()

        plate_delta_control = soControl(connection_with_steel_plate,
                                        variable=self.var_plate_delta,
                                        image=self._createImage('image084'),
                                        step=1,
                                        width=5,
                                        allowempty=False,
                                        selectmode='normal',
                                        round=2)
        plate_delta_control.pack(side=TOP, padx=3, pady=1)

        #

        separator = soSeparator(designed_bars, orient='horizontal')
        separator.pack(fill=X, pady=3)
        designed_id_label2 = soLabel(designed_bars, text='Permanent coefficients')
        designed_id_label2.pack()
        separator = soSeparator(designed_bars, orient='horizontal')
        separator.pack(fill=X, pady=3)

        def validate_kmod(x):
            try:
                x = float(x)
            except TypeError:
                return 1
            if x < 0.2:
                x = 0.2
            return x

        gamma_m_control = soControl(designed_bars,
                                    image=self._createImage('image001'),
                                    variable=self.var_gamma_m,
                                    step=0.1,
                                    width=5,
                                    allowempty=False,
                                    validatecmd=validate_0,
                                    selectmode='normal',
                                    round=2)
        gamma_m_control.pack(side=TOP)

        k_mod_control = soControl(designed_bars,
                                  image=self._createImage('image002'),
                                  variable=self.var_k_mod,
                                  step=0.1,
                                  width=5,
                                  allowempty=False,
                                  validatecmd=validate_kmod,
                                  selectmode='normal',
                                  round=2)
        k_mod_control.pack(side=TOP)

        separator = soSeparator(designed_bars, orient='horizontal')
        separator.pack(fill=X, pady=3)

        bending_check = soCheckbutton(designed_bars,
                                      text=u"Calculate bending and\nshearing of connection",
                                      variable=self.var_calc_bend_tens)
        bending_check.pack(side=TOP)

        axial_check = soCheckbutton(designed_bars,
                                    text=u"Axially loaded connectors",
                                    variable=self.var_calc_axially_loaded)
        axial_check.pack(side=TOP)

        # ! connection_pref_tab

        connection_pref_lab = soLabel(connection_pref_tab, text='Connectors settings')
        connection_pref_lab.pack()

        separator = soSeparator(connection_pref_tab, orient='horizontal')
        separator.pack(fill=X, pady=3)

        cb_frame = soFrame(connection_pref_tab)
        cb_frame.pack()

        connection_type_lab = soLabel(cb_frame, text='Connectors type: ')
        connection_type_lab.pack(side=LEFT)

        nail_type_cb = soComboBox(cb_frame,
                                  state='readonly',
                                  width=16,
                                  values=['Round Nails', 'Square/Grooved Nails', 'Bolts', 'Screws', 'Dowels',
                                          'Round Staples', 'Square Staples'],
                                  textvariable=self.var_nail_radio)
        nail_type_cb.pack(side=LEFT)

        separator = soSeparator(connection_pref_tab, orient='horizontal')
        separator.pack(fill=X, pady=3)

        self.two_sided_cb = soCheckbutton(connection_pref_tab,
                                          text=u"Connectors on both sides of connection",
                                          variable=self.var_two_sided)
        self.two_sided_cb.pack(side=TOP, anchor=W, padx=3, pady=1)

        self.predrill_cb = soCheckbutton(connection_pref_tab,
                                         text=u"Predrilled holes ",
                                         variable=self.var_predrilled_holes)
        self.predrill_cb.pack(side=TOP, anchor=W, padx=3, pady=1)

        def validate_below_1(x):
            try:
                x = float(x)
            except TypeError:
                return 1
            if x < 1.:
                x = 1
            return x

        dimensions_placeholder = soFrame(connection_pref_tab)
        dimensions_placeholder.pack(fill=X, padx=3, pady=1)

        # nails and other
        self.nail_control_frame = soLabelFrame(dimensions_placeholder, text='Connector dimensions [mm]')

        self.diameter_control = soControl(self.nail_control_frame,
                                          label='d =',
                                          variable=self.var_diameter,
                                          step=1,
                                          width=4,
                                          allowempty=False,
                                          validatecmd=validate_below_1,
                                          selectmode='normal')
        self.diameter_control.grid(row=1, column=1, padx=3, pady=1)

        self.nail_length_control = soControl(self.nail_control_frame,
                                             label='l =',
                                             variable=self.var_nail_length,
                                             step=1,
                                             width=5,
                                             allowempty=False,
                                             validatecmd=validate_below_1,
                                             selectmode='normal')
        self.nail_length_control.grid(row=1, column=2, padx=3, pady=1)

        def autol():
            if results.isCalculated():
                self.var_nail_length.set(floor(results.getResult('max_nail_length')))

        auto_a_l = soButton(self.nail_control_frame,
                            text='Auto max l',
                            command=autol)
        auto_a_l.grid(row=1, column=3, padx=3, pady=1, sticky='we')

        # bolts
        self.bolt_control_frame = soLabelFrame(dimensions_placeholder, text='Bolt settings')

        bolt_class = soComboBox(self.bolt_control_frame,
                                state='readonly',
                                width=4,
                                values=['4.6', '4.8', '5.6', '5.8', '6.8', '8.8', '10.9'],
                                textvariable=self.var_bolt_str)
        bolt_class.grid(row=1, column=2, padx=3, pady=1)

        bolt_diameter = soComboBox(self.bolt_control_frame,
                                   state='readonly',
                                   width=4,
                                   values=['M08', 'M10', 'M12', 'M16', 'M20', 'M22', 'M24',
                                           'M27', 'M30'],
                                   textvariable=self.var_boltd_str)
        bolt_diameter.grid(row=1, column=1, padx=3, pady=1)

        spacing_control_frame = soLabelFrame(connection_pref_tab, text='Connector spacing [mm]')
        spacing_control_frame.pack(side=TOP, anchor=W, padx=3, pady=1)
        self.a1_control = soControl(spacing_control_frame,
                                    image=self._createImage('image086'),
                                    variable=self.var_a1,
                                    step=1,
                                    width=4,
                                    allowempty=False,
                                    validatecmd=validate_below_1,
                                    selectmode='normal')
        self.a1_control.grid(row=1, column=1, padx=3, pady=1)

        self.a2_control = soControl(spacing_control_frame,
                                    image=self._createImage('image087'),
                                    variable=self.var_a2,
                                    step=1,
                                    width=4,
                                    allowempty=False,
                                    validatecmd=validate_below_1,
                                    selectmode='normal')
        self.a2_control.grid(row=1, column=2, padx=3, pady=1)

        def autoa():
            if results.isCalculated():
                self.var_a1.set(ceil(float(results.getResult('a1_lim'))))
                self.var_a2.set(ceil(float(results.getResult('a2_lim'))))

        auto_a_button = soButton(spacing_control_frame,
                                 text='Auto min',
                                 command=autoa)
        auto_a_button.grid(row=1, column=3, padx=3, pady=1)

        n_control_frame = soLabelFrame(connection_pref_tab, text='Connectors amount')
        n_control_frame.pack(fill=X, anchor=W, padx=3, pady=1)

        n_control = soControl(n_control_frame,
                              image=self._createImage('image003'),
                              variable=self.var_num_of_fasteners,
                              step=1,
                              width=4,
                              allowempty=False,
                              validatecmd=validate_below_1,
                              selectmode='normal')
        n_control.grid(row=1, column=1, padx=3, pady=1)

        nr_control = soControl(n_control_frame,
                               image=self._createImage('image004'),
                               variable=self.var_num_of_rows,
                               step=1,
                               width=4,
                               allowempty=False,
                               validatecmd=validate_below_1,
                               selectmode='normal')
        nr_control.grid(row=1, column=2, padx=3, pady=1)

        def auton():
            if results.isCalculated():
                self.var_num_of_rows.set(results.getResult('max_num_of_rows'))
                self.var_num_of_fasteners.set(results.getResult('max_num_of_fasteners'))

        auto_n = soButton(n_control_frame,
                          text='Auto max',
                          command=auton)
        auto_n.grid(row=1, column=3, padx=3, pady=1, sticky='we')

        def validate_theta(x):
            try:
                x = float(x)
            except TypeError:
                return 45
            if x < 0.:
                x = 0
            if x > 90:
                x = 90
            return x

        self.theta_control = soControl(connection_pref_tab,
                                       image=self._createImage('image005'),
                                       variable=self.var_theta,
                                       step=1,
                                       width=5,
                                       allowempty=False,
                                       validatecmd=validate_theta,
                                       selectmode='normal',
                                       state=DISABLED)
        self.theta_control.pack(side=TOP, anchor=W, padx=3, pady=1)

        f_u_frame = soLabelFrame(connection_pref_tab, text='Connector tensile strength')
        f_u_frame.pack(fill=X, anchor=W, padx=3, pady=1)

        self.switch_fu = dnComponentDlg.SwitchFrame(f_u_frame)
        self.switch_fu.pack(side=LEFT)

        self.f_u_cont_frame = soFrame(self.switch_fu)
        self.f_u_cont_frame.pack()
        self.switch_fu.add(self.f_u_cont_frame)

        self.f_u_control = soControl(self.f_u_cont_frame,
                                     image=self._createImage('image006'),
                                     variable=self.var_f_u,
                                     step=1,
                                     width=5,
                                     allowempty=False,
                                     validatecmd=validate_below_1,
                                     selectmode='normal')
        self.f_u_control.pack(side=LEFT, padx=3, pady=1)

        self.f_u_val_frame = soFrame(self.switch_fu)
        self.f_u_val_frame.pack()
        self.switch_fu.add(self.f_u_val_frame)

        self.f_u_val = dnComponentDlg.ResultValue(self.f_u_val_frame, format='%.f',
                                                  lImage=self._createImage('image006'))
        self.f_u_val.pack(side=LEFT, padx=3, pady=1)

        self.switch_fu.switch(0)

    def create_tab1(self, tab):

        results = self.getCompObj().getResults()

        frame = soFrame(tab)
        frame.pack()
        master_frame = soFrame(frame)
        master_frame.pack(fill=BOTH)

        top_frame = soFrame(master_frame)
        top_frame.pack(fill=BOTH, padx=1, pady=1)

        bottom_frame = soFrame(master_frame)
        bottom_frame.pack(padx=1, pady=1, expand=1)

        left_frame_spacings = soFrame(top_frame)
        left_frame_spacings.pack(side=LEFT, padx=1, pady=1)

        a_frame = soLabelFrame(left_frame_spacings, text='Spacings and limits [mm]')
        a_frame.pack(side=TOP, padx=1, pady=1)

        self.a1comp = dnComponentDlg.Comparison(a_frame,
                                                lImage=self._createImage('image017'),
                                                rImage=self._createImage('image018'))

        self.a1comp.pack(side=TOP)

        self.a2comp = dnComponentDlg.Comparison(a_frame,
                                                lImage=self._createImage('image019'),
                                                rImage=self._createImage('image020'))
        self.a2comp.pack(side=TOP)

        self.a3tcomp = dnComponentDlg.Comparison(a_frame,
                                                 lImage=self._createImage('image021'),
                                                 rImage=self._createImage('image022'))
        self.a3tcomp.pack(side=TOP)

        self.a3ccomp = dnComponentDlg.Comparison(a_frame,
                                                 lImage=self._createImage('image023'),
                                                 rImage=self._createImage('image024'))
        self.a3ccomp.pack(side=TOP)

        self.a4tcomp = dnComponentDlg.Comparison(a_frame,
                                                 lImage=self._createImage('image025'),
                                                 rImage=self._createImage('image026'))
        self.a4tcomp.pack(side=TOP)

        self.a4ccomp = dnComponentDlg.Comparison(a_frame,
                                                 lImage=self._createImage('image027'),
                                                 rImage=self._createImage('image028'))
        self.a4ccomp.pack(side=TOP)

        self.penetration_comp = dnComponentDlg.Comparison(a_frame,
                                                          lImage=self._createImage('image069'),
                                                          rImage=self._createImage('image070'))
        self.penetration_comp.pack(side=TOP)

        forces_f = soLabelFrame(left_frame_spacings, relief='groove', text='Forces in connection [kN / kNm]')
        forces_f.pack(side=TOP, fill=BOTH, padx=1, pady=1)

        def forces_check():
            self.forces_switch_frame.switch(self.var_forces_chb.get())

        # forces_f

        forces_check = soCheckbutton(forces_f,
                                     text=u"Enter own forces",
                                     variable=self.var_forces_chb,
                                     command=forces_check)
        forces_check.pack(side=TOP)

        self.forces_switch_frame = dnComponentDlg.SwitchFrame(forces_f)
        self.forces_switch_frame.pack()

        forces_disp_frame = soFrame(self.forces_switch_frame)
        forces_disp_frame.pack()

        forces_enter_frame = soFrame(self.forces_switch_frame)
        forces_enter_frame.pack()

        self.forces_switch_frame.add(forces_disp_frame)
        self.forces_switch_frame.add(forces_enter_frame)

        self.forces_switch_frame.switch(0)

        # disp frame

        self.axial_force_val = dnComponentDlg.ResultValue(forces_disp_frame, format='%.2f',
                                                          lImage=self._createImage('image062'))
        self.axial_force_val.pack(padx=2, pady=2)

        self.shear_force_val = dnComponentDlg.ResultValue(forces_disp_frame, format='%.2f',
                                                          lImage=self._createImage('image063'))
        self.shear_force_val.pack(padx=2, pady=2)

        self.bending_moment_val = dnComponentDlg.ResultValue(forces_disp_frame, format='%.2f',
                                                             lImage=self._createImage('image064'))
        self.bending_moment_val.pack(padx=2, pady=2)

        # entry frame

        self.axial_control = soControl(forces_enter_frame,
                                       image=self._createImage('image062'),
                                       variable=self.var_axial_f,
                                       step=1.,
                                       width=8,
                                       allowempty=False,
                                       selectmode='normal')
        self.axial_control.pack(padx=2, pady=1)

        self.shear_control = soControl(forces_enter_frame,
                                       image=self._createImage('image063'),
                                       variable=self.var_shear_f,
                                       step=1.,
                                       width=8,
                                       allowempty=False,
                                       selectmode='normal')
        self.shear_control.pack(padx=2, pady=1)

        self.moment_control = soControl(forces_enter_frame,
                                        image=self._createImage('image064'),
                                        variable=self.var_bending_m,
                                        step=1.,
                                        width=8,
                                        allowempty=False,
                                        selectmode='normal')
        self.moment_control.pack(side=LEFT, padx=3, pady=1)

        self.axial_connect = soControl(forces_f,
                                       image=self._createImage('image092'),
                                       variable=self.var_f_ax_ed,
                                       step=1.,
                                       width=8,
                                       allowempty=False,
                                       selectmode='normal')
        self.axial_connect.pack(side=TOP, padx=3, pady=1)

        if self.var_calc_axially_loaded.get() == 1:
            self.axial_connect['state'] = NORMAL
        else:
            self.axial_connect['state'] = DISABLED

        axialcap_f = soLabelFrame(left_frame_spacings, text='Combined lateral-axial capacity')
        axialcap_f.pack(side=TOP, padx=1, pady=1, expand=1, fill=BOTH)

        # if self.var_nail_radio.get() == 'Round Nails' or self.var_nail_radio.get() == 'Round Staples':
        #     self.axial_cap_comp['lImage'] = self._createImage('image094')
        # else:
        #     self.axial_cap_comp['lImage'] = self._createImage('image093')

        self.axial_cap_comp = dnComponentDlg.Comparison(axialcap_f,
                                                        lImage=self._createImage('image093'),
                                                        lFormat='%.2f', rFormat='%.2f')
        self.axial_cap_comp.pack(padx=2, pady=2)

        right_frame_results = soFrame(top_frame)
        right_frame_results.pack(side=BOTTOM, expand=1, fill=BOTH, padx=1, pady=1)

        # Properties

        res_top_frame = soFrame(right_frame_results)
        res_top_frame.pack(fill=BOTH, expand=1)

        ele_frame = soLabelFrame(res_top_frame, text='Properties')
        ele_frame.pack(side=LEFT, fill=Y, padx=1, pady=1)
        ele_inf = soFrame(ele_frame)
        ele_inf.pack()

        self.connection_type_label_val = soLabel(ele_inf,
                                                 text=results.getResult('connection_type_str'), justify='center')
        self.connection_type_label_val.grid(row=0, column=1, columnspan=2, padx=2, pady=1)
        # connection_type_label updated by designed_combo_change + connect_radio

        soSeparator(ele_inf, orient='horizontal').grid(row=1, column=1, columnspan=2, sticky='we')

        self.n_sp_val = dnComponentDlg.ResultValue(ele_inf, format='%.f', lLabel='Shear planes =')
        self.n_sp_val.grid(row=2, column=1, columnspan=2, padx=2, pady=1)

        self.t1_val = dnComponentDlg.ResultValue(ele_inf, format='%.f', lImage=self._createImage('image029'),
                                                 rImage=self._createImage('image075'))
        self.t1_val.grid(row=3, column=1, padx=2, pady=1)

        self.t2_val = dnComponentDlg.ResultValue(ele_inf, format='%.f', lImage=self._createImage('image030'),
                                                 rImage=self._createImage('image075'))
        self.t2_val.grid(row=3, column=2, padx=2, pady=1)

        self.f_h_1 = dnComponentDlg.ResultValue(ele_inf, format='%.2f', lImage=self._createImage('image031'),
                                                rImage=self._createImage('image073'))
        self.f_h_1.grid(row=4, column=1, columnspan=2)

        self.f_h_2 = dnComponentDlg.ResultValue(ele_inf, format='%.2f', lImage=self._createImage('image032'),
                                                rImage=self._createImage('image073'))
        self.f_h_2.grid(row=5, column=1, columnspan=2)

        self.beta_val = dnComponentDlg.ResultValue(ele_inf, format='%.2f', lImage=self._createImage('image071'))
        self.beta_val.grid(row=6, column=1, columnspan=2, padx=2, pady=1)

        self.kef_val = dnComponentDlg.ResultValue(ele_inf, format='%.2f', lImage=self._createImage('image088'))
        self.kef_val.grid(row=7, column=1, padx=2, pady=1)

        self.nef_val = dnComponentDlg.ResultValue(ele_inf, format='%.2f', lImage=self._createImage('image072'))
        self.nef_val.grid(row=7, column=2, padx=2, pady=1)

        self.myrk_val = dnComponentDlg.ResultValue(ele_inf, format='%.f', lImage=self._createImage('image033'),
                                                   rImage=self._createImage('image076'))
        self.myrk_val.grid(row=8, column=1, columnspan=2, padx=2, pady=1)

        self.f_axrk_val = dnComponentDlg.ResultValue(ele_inf, format='%.f',
                                                     lImage=self._createImage('image007'),
                                                     rImage=self._createImage('image074'))
        self.f_axrk_val.grid(row=9, column=1, columnspan=2, padx=2, pady=1)

        # bend_f

        # forces_check = soCheckbutton(self.bend_help_f,
        #                              text=u"Ignore forces sign (max M)",
        #                              variable=self.var_forces_ignore_sign)
        # forces_check.pack(padx=2, pady=2)

        bend_f = soLabelFrame(res_top_frame, relief='groove', text='Bending forces\ncomponents')
        bend_f.pack(fill=BOTH, padx=1, pady=1, expand=1)

        self.bending_switch_frame = dnComponentDlg.SwitchFrame(bend_f)
        self.bending_switch_frame.pack()

        self.bending_coef = soFrame(self.bending_switch_frame)
        self.bending_coef.pack()

        self.nobend = soFrame(self.bending_switch_frame)
        self.nobend.pack(fill=BOTH)

        self.bending_switch_frame.add(self.bending_coef)
        self.bending_switch_frame.add(self.nobend)

        self.bending_switch_frame.switch(1)

        self.x_max_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.2f',
                                                    lImage=self._createImage('image077'),
                                                    rImage=self._createImage('image075'))
        self.x_max_val.pack(padx=2, pady=2)

        self.y_max_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.2f',
                                                    lImage=self._createImage('image078'),
                                                    rImage=self._createImage('image075'))
        self.y_max_val.pack(padx=2, pady=2)

        self.f_m_d_max_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.f',
                                                        lImage=self._createImage('image065'),
                                                        rImage=self._createImage('image074'))
        self.f_m_d_max_val.pack(padx=2, pady=2)

        self.f_h_d_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.f',
                                                    lImage=self._createImage('image066'),
                                                    rImage=self._createImage('image074'))
        self.f_h_d_val.pack(padx=2, pady=2)

        self.f_v_d_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.f',
                                                    lImage=self._createImage('image067'),
                                                    rImage=self._createImage('image074'))
        self.f_v_d_val.pack(padx=2, pady=2)

        self.f_d_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.f',
                                                  lImage=self._createImage('image068'),
                                                  rImage=self._createImage('image074'))
        self.f_d_val.pack(padx=2, pady=2)

        self.angle_to_grain_val = dnComponentDlg.ResultValue(self.bending_coef, format='%.2f',
                                                             lImage=self._createImage('image079'),
                                                             rImage=self._createImage('image080'))
        self.angle_to_grain_val.pack(padx=2, pady=2)

        self.nobendlabel = soLabel(self.nobend, text='Bending and shearing is not calculated', justify='center')
        self.nobendlabel.pack(expand=1, padx=9, pady=2)

        # capacity_f

        capacity_f = soLabelFrame(right_frame_results, relief='groove', text='Capacities [kN]')
        capacity_f.pack(side=BOTTOM, fill=BOTH, padx=1, pady=1)

        axial_frame = soFrame(capacity_f)
        axial_frame.pack(side=LEFT, fill=BOTH, expand=1)

        self.final_capacity = dnComponentDlg.Comparison(axial_frame,
                                                        lImage=self._createImage('image012'))
        self.final_capacity.pack(padx=2, pady=2)

        self.final_cap_comp = dnComponentDlg.Comparison(axial_frame,
                                                        lImage=self._createImage('image013'),
                                                        rImage=self._createImage('image014'),
                                                        lFormat='%.2f', rFormat='%.2f')
        self.final_cap_comp.pack(padx=2, pady=2)

        self.f90check = dnComponentDlg.Comparison(axial_frame,
                                                  lImage=self._createImage('image015'),
                                                  rImage=self._createImage('image016'),
                                                  lFormat='%.2f', rFormat='%.2f')
        self.f90check.pack(padx=2, pady=2)

        self.bending_hiddenframe = dnComponentDlg.HiddenFrame(capacity_f)
        self.bending_hiddenframe.pack(side=LEFT, padx=3, pady=3)
        bending_frame = soFrame(self.bending_hiddenframe)
        self.bending_hiddenframe.insert(bending_frame)

        if self.var_calc_bend_tens.get() == 1:
            self.bending_hiddenframe.show()
        else:
            self.bending_hiddenframe.hide()

        self.final_capacitybending = dnComponentDlg.Comparison(bending_frame,
                                                               lImage=self._createImage('image089'))
        self.final_capacitybending.pack(padx=2, pady=2)

        self.final_cap_compbending = dnComponentDlg.Comparison(bending_frame,
                                                               lImage=self._createImage('image068'),
                                                               rImage=self._createImage('image091'),
                                                               lFormat='%.2f', rFormat='%.2f')
        self.final_cap_compbending.pack(padx=2, pady=2)

        tree_frame = soFrame(bottom_frame, relief='groove', borderwidth=1)
        tree_frame.pack(fill=X, expand=1)

        self.treeview = ttk.Treeview(tree_frame, height=3, selectmode='none')
        self.treeview.column('#0', minwidth=638, width=638)
        self.treeview.heading('#0', text="Capacities for respective failure modes (red - deciding)", anchor='center')
        ysb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=ysb.set)
        self.treeview.grid(row=0, column=0)
        ysb.grid(row=0, column=1, sticky='ns')
        ttk.Style().layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        ttk.Style().configure('Treeview', rowheight=30)
        #

    def create_info(self, tab):
        master_frame = Frame(tab)
        master_frame.pack(fill=BOTH)

        soLabel(master_frame, text='adrian kowalczewski 2014', justify='center').pack(side=TOP, anchor=W, padx=3,
                                                                                      pady=1)

    # noinspection PyUnboundLocalVariable
    def update_canvas(self):
        self.canvas.delete(ALL)
        self.canvas.set_default()

        # data
        comp_obj = self.getCompObj()
        node_object = comp_obj.getItem()
        node_number = node_object.getNumber()
        comp_res = comp_obj.getResults()
        elements = node_object.getElements(node='both')

        # picked bars
        designed = int(self.var_designed_id_str.get())
        other = int(self.var_other_id_str.get())

        #angles
        angles_dict = {}
        for p in elements:
            if p.getNodesNums()[0] != node_number:
                angles_dict[p.getNumber()] = p.getAngle() + pi
            else:
                angles_dict[p.getNumber()] = p.getAngle()
        for p in angles_dict:
            if round(angles_dict[p] - 2 * pi) > -0.01:
                angles_dict[p] -= 2 * pi

        elements_tags = (soMetricCanvas.TAB_FIT_TO_VIEW, soMetricCanvas.TAB_ROTATE,
                         soMetricCanvas.TAB_MOVE, soMetricCanvas.TAB_SCALE,)
        text_tags = [soMetricCanvas.TAB_FIT_TO_VIEW, soMetricCanvas.TAB_ROTATE, ]

        def rect(r, theta_):
            theta_ = -theta_ + pi / 2
            x_ = r * cos(theta_)
            y_ = r * sin(theta_)
            return x_, y_

        if comp_res.isCalculated():
            other_element_num = comp_res.getResult('other_element_num')

        # Draw all elements
        delta_x = 0
        delta_y = 0
        h_list = []
        for i in range(len(elements)):
            h = elements[i].getComplexProfile().get_H()
            h_list.append(h)
            alfa = angles_dict[elements[i].getNumber()]
            gam = alfa + pi / 2
            theta = alfa - pi / 2
            ele_l = 2000
            x0, y0 = rect(h / 2, gam)
            x1, y1 = rect(h / 2, theta)
            xc, yc = rect(ele_l, alfa)
            x2 = x0 + xc
            y2 = y0 + yc
            x3 = x1 + xc
            y3 = y1 + yc

            # colors, selected elements coordinates
            if elements[i].getComplexProfile().getPrincipalMaterial().getType() == 'Stal':
                fill = '#c4fffa'
            else:
                fill = '#f0e480'

            if comp_res.isCalculated():
                if elements[i].getNumber() == other_element_num:
                    oec = x0, y0, x1, y1, x3, y3, x2, y2  # oec = other paired element coordinates,
                    # draw him only when all is ok
            if elements[i].getNumber() == designed:
                dc = x0, y0, x1, y1, x3, y3, x2, y2  # dc = designed coordinates, draw allways
                designed_alfa = alfa
                designed_gam = gam
                designed_theta = theta
                if elements[i].getComplexProfile().getPrincipalMaterial().getType() == 'Stal':
                    fill_d = '#167f7f'
                    fill = '#167f7f'
                else:
                    fill_d = '#beab0d'
                    fill = '#beab0d'
            if elements[i].getNumber() == other and self.var_connect_to_radio.get() == 0:
                oc = x0, y0, x1, y1, x3, y3, x2, y2  # oc = other coordinates, draw allways
                if elements[i].getComplexProfile().getPrincipalMaterial().getType() == 'Stal':
                    fill_o = '#9bd5d5'
                    fill = '#9bd5d5'
                else:
                    fill_o = '#d8ca58'
                    fill = '#d8ca58'
            self.canvas.create_polygon(x0, y0, x1, y1, x3, y3, x2, y2, fill=fill, outline='grey', tags=elements_tags)

        if comp_res.isCalculated():

            # connection to other element
            if self.var_connect_to_radio.get() == 0:
                # Draw selected/other element on top of previous elements
                self.canvas.create_polygon(oec[0], oec[1], oec[2], oec[3], oec[4], oec[5], oec[6], oec[7], fill=fill_o,
                                           outline='black', tags=elements_tags)
                self.canvas.create_polygon(oc[0], oc[1], oc[2], oc[3], oc[4], oc[5], oc[6], oc[7], fill=fill_o,
                                           outline='black', tags=elements_tags)
                self.canvas.create_polygon(dc[0], dc[1], dc[2], dc[3], dc[4], dc[5], dc[6], dc[7], fill=fill_d,
                                           outline='black', tags=elements_tags)

                # Draw connection area - treat edges of area as
                # 2x2 bolts with area witdth/length spacing. get their coords
                h_0_projection = comp_res.getResult('h_0_projection')
                h_1_projection = comp_res.getResult('h_1_projection')
                if comp_res.getResult('flat_connection'):
                    x_coord, y_coord = calc_bound(2,
                                                  h_0_projection, angles_dict[designed] - pi / 2,
                                                  2,
                                                  h_1_projection, angles_dict[designed])
                else:
                    x_coord, y_coord = calc_bound(2,
                                                  h_0_projection, angles_dict[other],
                                                  2,
                                                  h_1_projection, angles_dict[designed])
                self.canvas.create_polygon(x_coord[0], y_coord[0], x_coord[1], y_coord[1], x_coord[3], y_coord[3],
                                           x_coord[2], y_coord[2], fill=fill_d, outline='red', tags=elements_tags)

                # calculate coords for further use in drawing connectors
                coords, x_coord, y_coord, radius_list, radius_sum = calc_connectors_with_displacement(
                    self.var_num_of_fasteners.get(),
                    self.var_a1.get(),
                    angles_dict[designed],
                    self.var_num_of_rows.get(),
                    self.var_a2.get(),
                    angles_dict[other],
                    0,
                    0)

            # connection to steel plate
            else:
                # draw designed element
                self.canvas.create_polygon(dc[0], dc[1], dc[2], dc[3], dc[4], dc[5], dc[6], dc[7], fill=fill_d,
                                           outline='black', tags=elements_tags)
                # draw plates on all elements
                plate_l = self.var_plate_l.get()
                delta = self.var_plate_delta.get()
                for i in range(len(elements)):
                    h = min(self.var_plate_h.get(), elements[i].getComplexProfile().get_H())
                    alfa = angles_dict[elements[i].getNumber()]
                    gam = alfa + pi / 2
                    theta = alfa - pi / 2
                    x0, y0 = rect(h / 2, gam)
                    x1, y1 = rect(h / 2, theta)
                    xc, yc = rect(plate_l, alfa)
                    x2 = x0 + xc
                    y2 = y0 + yc
                    x3 = x1 + xc
                    y3 = y1 + yc

                    # draw steel plate, if its inside, dash it
                    if comp_res.getResult('two_profiles_element_id') == 0:
                        self.canvas.create_polygon(x0, y0, x1, y1, x3, y3, x2, y2, fill='#c4fffa', outline='',
                                                   tags=elements_tags, dash=(1, 1))
                    else:
                        if elements[i].getComplexProfile().getPrincipalMaterial().getType() == 'Stal':
                            continue
                        self.canvas.create_polygon(x0, y0, x1, y1, x3, y3, x2, y2, fill='#167f7f', outline='',
                                                   tags=elements_tags)
                # plate coordinates
                h = self.var_plate_h.get()
                alfa = designed_alfa
                gam = designed_gam
                theta = designed_theta
                x0, y0 = rect(h / 2, gam)
                x1, y1 = rect(h / 2, theta)
                xc, yc = rect(plate_l, alfa)
                x2 = x0 + xc
                y2 = y0 + yc
                x3 = x1 + xc
                y3 = y1 + yc

                # plate displacement vector
                delta_x = sin(designed_alfa) * delta
                delta_y = cos(designed_alfa) * delta
                x0 += delta_x
                x1 += delta_x
                x2 += delta_x
                x3 += delta_x
                y0 += delta_y
                y1 += delta_y
                y2 += delta_y
                y3 += delta_y

                # draw steel plate, if its inside, dash it
                if comp_res.getResult('two_profiles_element_id') == 0:
                    self.canvas.create_polygon(x0, y0, x1, y1, x3, y3, x2, y2, fill='#c4fffa', outline='gray',
                                               tags=elements_tags, dash=(1, 1))
                else:
                    self.canvas.create_polygon(x0, y0, x1, y1, x3, y3, x2, y2, fill='#167f7f', outline='black',
                                               tags=elements_tags)

                # calculate coords for further use in drawing connectors
                coords, x_coord, y_coord, radius_list, radius_sum = calc_connectors_with_displacement(
                    self.var_num_of_fasteners.get(),
                    self.var_a1.get(),
                    angles_dict[designed],
                    self.var_num_of_rows.get(),
                    self.var_a2.get(),
                    angles_dict[designed],
                    delta,
                    plate_l)

        # Draw connectors
        if comp_res.isCalculated():
            d = comp_res.getResult('d')

            def draw_connector(xcoord, ycoord, d_, color, out):  # draw bolts with coords and d only
                d_ *= 1.5  # graphical representation
                self.canvas.create_oval(xcoord - d_ / 2, ycoord + d_ / 2, xcoord + d_ / 2, ycoord - d_ / 2,
                                        fill=color, outline=out, tags=elements_tags)

            for coord in coords:
                draw_connector(coord[0], coord[1], d, 'black', 'black')
            # extremal connector (in bending)
            if self.var_calc_bend_tens.get() == 1:
                x_max = comp_res.getResult('x_max')
                y_max = comp_res.getResult('y_max')
                draw_connector(x_max, y_max, d, 'red', 'red')

        # draw bar numbers
        for i in range(len(elements)):
            alfa = angles_dict[elements[i].getNumber()]
            x_text, y_text = rect(max(max(h_list), self.var_plate_l.get()) * 1.10, alfa)
            text_color = 'black'
            if elements[i].getNumber() == designed:
                text_color = '#cc0000'
                if self.var_connect_to_radio.get() == 1:
                    x_text += delta_x
                    y_text += delta_y
            self.canvas.create_text(x_text, y_text, font=('Arial', 10),
                                    text=str(elements[i].getNumber()), fill=text_color, tags=text_tags)

        # fit to view
        boundary = max(max(h_list), self.var_plate_l.get()) * 1.3
        exterior_boundary_tags = (soMetricCanvas.TAB_EXTERIOR_BOUNDARY, soMetricCanvas.TAB_FIT_TO_VIEW)
        if self.var_connect_to_radio.get() == 0:
            self.canvas.create_polygon(-boundary, -boundary,
                                       boundary, -boundary,
                                       boundary, boundary,
                                       -boundary, boundary,
                                       width=5, fill='', tags=exterior_boundary_tags)
        else:
            self.canvas.create_polygon(-boundary + delta_x, -boundary + delta_y,
                                       boundary + delta_x, -boundary + delta_y,
                                       boundary + delta_x, boundary + delta_y,
                                       -boundary + delta_x, boundary + delta_y,
                                       width=5, fill='', tags=exterior_boundary_tags)
        self.canvas.fit_to_view()
        # self.canvas.postscript(file="gener_canvas.ps", colormode='color')
        # process = subprocess.Popen(["ps2pdf", "gener_canvas.ps", "gener_canvas.pdf"], shell=True)
        # process.wait()
        # img = PIL.Image.open("gener_canvas.ps")
        # img.save("GDZIEJSTES.bmp")

    def update_panel(self):

        node_object = self.getCompObj().getItem()
        elements = node_object.getElements(node='both')
        self.bars_li = []
        for n in range(len(elements)):
            self.bars_li.append(elements[n].getNumber())

        self.designed_id_combo['values'] = self.bars_li
        self.other_id_combo['values'] = self.bars_li

        component_results = self.getCompObj().getResults()

        if self.var_connect_to_radio.get() == 1:
            self.designed_bars_switchframe.switch(1)
        else:
            self.designed_bars_switchframe.switch(0)

        if self.var_nail_radio.get() == 'Bolts':
            self.switch_fu.switch(1)
            self.two_sided_cb['state'] = DISABLED
            self.var_two_sided.set(0)
            self.predrill_cb['state'] = DISABLED
            self.var_predrilled_holes.set(1)
            self.bolt_control_frame.pack(fill=X)
            self.nail_control_frame.pack_forget()
        else:
            self.switch_fu.switch(0)
            self.two_sided_cb['state'] = NORMAL
            self.predrill_cb['state'] = NORMAL
            self.bolt_control_frame.pack_forget()
            self.nail_control_frame.pack(fill=X)

        if self.var_nail_radio.get() == 'Round Staples' or self.var_nail_radio.get() == 'Square Staples':
            self.theta_control['state'] = NORMAL
            self.f_u_control['state'] = DISABLED
            self.var_f_u.set(800)
        else:
            self.theta_control['state'] = DISABLED
            self.f_u_control['state'] = NORMAL

        if component_results.isCalculated():
            self.f_u_val.setValue(component_results.getResult('f_u'))
            self.plate_t_val.setValue(component_results.getResult('plate_t'))
        else:
            self.f_u_val.clear()
            self.plate_t_val.clear()

        if component_results.getResult('two_profiles_element_id') == 1:
            self.plate_t_switch_frame.switch(0)
        else:
            self.plate_t_switch_frame.switch(1)

        if component_results.getResult('steel_plate_inside') is False and self.var_force_plate_inside.get() == 1:
            self.plate_t_switch_frame.switch(0)

        if component_results.getResult('flat_connection'):
            self.l_control_hiddenframe.show()
        else:
            self.l_control_hiddenframe.hide()

        self.update_canvas()

    def update_tab1(self):

        component_results = self.getCompObj().getResults()

        if component_results.isCalculated():

            self.connection_type_label_val['text'] = component_results.getResult('connection_type_str')

            # if self.var_nail_radio.get() == 'Round Nails' or self.var_nail_radio.get() == 'Round Staples':
            #     self.axial_cap_comp['lImage'] = self._createImage('image094')
            # else:
            #     self.axial_cap_comp['lImage'] = self._createImage('image093')

            if self.var_calc_bend_tens.get() == 1:
                self.bending_hiddenframe.show()
                self.bending_switch_frame.switch(0)
            else:
                self.bending_hiddenframe.hide()
                self.bending_switch_frame.switch(1)

            if self.var_calc_axially_loaded.get() == 1:
                self.axial_connect['state'] = NORMAL
            else:
                self.axial_connect['state'] = DISABLED

            # spac
            self.a1comp.setValues(component_results.getResult('a1_lim'), component_results.getResult('self.a1'))
            self.a2comp.setValues(component_results.getResult('a2_lim'), component_results.getResult('self.a2'))
            self.a3tcomp.setValues(component_results.getResult('a3t'),
                                   component_results.getResult('parallel_to_end'))
            self.a3ccomp.setValues(component_results.getResult('a3c'),
                                   component_results.getResult('parallel_to_end'))
            self.a4tcomp.setValues(component_results.getResult('a4t'),
                                   component_results.getResult('perpendicular_to_end'))
            self.a4ccomp.setValues(component_results.getResult('a4c'),
                                   component_results.getResult('perpendicular_to_end'))
            self.penetration_comp.setValues(component_results.getResult('penetration_limit'),
                                            component_results.getResult('pointside_penetration'))
            # prop
            self.n_sp_val.setValue(component_results.getResult('shear_planes'))
            self.t1_val.setValue(component_results.getResult('t1'))
            self.t2_val.setValue(component_results.getResult('t2'))
            self.f_h_1.setValue(component_results.getResult('f_h_k_list')[0])
            self.f_h_2.setValue(component_results.getResult('f_h_k_list')[1])
            self.beta_val.setValue(component_results.getResult('beta'))
            if component_results.getResult('steel_in_connection'):
                if component_results.getResult('steel_ele_id') == 0:
                    self.f_h_1.clear()
                    self.beta_val.clear()
                else:
                    self.f_h_2.clear()
                    self.beta_val.clear()
            self.kef_val.setValue(component_results.getResult('k_ef'))
            self.myrk_val.setValue(component_results.getResult('myrk'))
            self.nef_val.setValue(component_results.getResult('nef'))
            # forces
            self.axial_force_val.setValue(component_results.getResult('axial_force') / 1000)
            self.shear_force_val.setValue(component_results.getResult('shear_force') / 1000)
            self.bending_moment_val.setValue(component_results.getResult('bending_moment') / 1000 / 1000)
            self.f_axrk_val.setValue(component_results.getResult('f_axrk'))
            # bending
            if self.var_calc_bend_tens.get() == 1:
                self.x_max_val.setValue(component_results.getResult('x_max'))
                self.y_max_val.setValue(component_results.getResult('y_max'))
                self.f_m_d_max_val.setValue(component_results.getResult('f_m_d_max'))
                self.f_h_d_val.setValue(component_results.getResult('f_h_d'))
                self.f_v_d_val.setValue(component_results.getResult('f_v_d'))
                self.f_d_val.setValue(component_results.getResult('f_d'))
                self.angle_to_grain_val.setValue(component_results.getResult('angle_to_grain'))
            else:
                self.x_max_val.clear()
                self.y_max_val.clear()
                self.f_m_d_max_val.clear()
                self.f_h_d_val.clear()
                self.f_v_d_val.clear()
                self.f_d_val.clear()
                self.angle_to_grain_val.clear()
            # capacites
            self.axial_cap_comp.setValues(component_results.getResult('axial_ratio'), 1)
            self.final_capacity.setValues(component_results.getResult('ratio'), 1)
            self.final_cap_comp.setValues(component_results.getResult('f_ed') / 1000,
                                          component_results.getResult('f_vefrd') / 1000)
            self.f90check.setValues(component_results.getResult('f_v_ed'),
                                    component_results.getResult('f_90_rd'))
            self.final_capacitybending.setValues(component_results.getResult('ratiobend'), 1)
            self.final_cap_compbending.setValues(component_results.getResult('f_d') / 1000,
                                                 component_results.getResult('f_vefrdbend') / 1000)

        else:
            self.a1comp.clear()
            self.a2comp.clear()
            self.a3tcomp.clear()
            self.a3ccomp.clear()
            self.a4tcomp.clear()
            self.a4ccomp.clear()
            self.penetration_comp.clear()

            self.n_sp_val.clear()
            self.t1_val.clear()
            self.t2_val.clear()
            self.f_h_1.clear()
            self.f_h_2.clear()
            self.myrk_val.clear()
            self.beta_val.clear()
            self.kef_val.clear()
            self.nef_val.clear()

            self.final_capacity.clear()
            self.final_cap_comp.clear()
            self.f90check.clear()
            self.final_capacitybending.clear()
            self.final_cap_compbending.clear()

            self.axial_force_val.clear()
            self.shear_force_val.clear()
            self.bending_moment_val.clear()
            self.f_axrk_val.clear()

            self.x_max_val.clear()
            self.y_max_val.clear()
            self.f_m_d_max_val.clear()
            self.f_h_d_val.clear()
            self.f_v_d_val.clear()
            self.f_d_val.clear()
            self.angle_to_grain_val.clear()

        #update treeview
        # Failure mode image dictionaties
        timber_images_dict = {'a': 'image036',
                              'b': 'image037',
                              'c': 'image038',
                              'd': 'image039',
                              'e': 'image040',
                              'f': 'image041',
                              'g': 'image042',
                              'h': 'image043',
                              'j': 'image044',
                              'k': 'image045'}
        steel_images_dict = {'a': 'image046',
                             'b': 'image047',
                             'c': 'image048',
                             'd': 'image049',
                             'e': 'image050',
                             'a+c': 'image051',
                             'b+e': 'image052',
                             'f': 'image053',
                             'g': 'image054',
                             'h': 'image055',
                             'j': 'image056',
                             'k': 'image057',
                             'l': 'image058',
                             'm': 'image059',
                             'j+l': 'image060',
                             'k+m': 'image061'}

        if component_results.isCalculated():

            children = self.treeview.get_children()
            for item in children:
                self.treeview.delete(item)
            if component_results.getResult('steel_in_connection'):
                img_dict = steel_images_dict
            else:
                img_dict = timber_images_dict
            f_vrk_un = component_results.getResult('f_vrk')
            f_vrk = collections.OrderedDict(sorted(f_vrk_un.items()))
            i = 0
            for key in f_vrk.iterkeys():
                if key == component_results.getResult('min(f_vrk)'):
                    self.treeview.insert('', i, '', image=self._createImage(img_dict[f_vrk[key]]), text=str(round(key)),
                                         tags='red')
                else:
                    self.treeview.insert('', i, '', image=self._createImage(img_dict[f_vrk[key]]), text=str(round(key)))

                i += 1
            self.treeview.tag_configure('red', foreground='red')

    def update_info(self):

        pass

    def getSize(self):
        return 730, 700


class PolaczenieDrewniane(dnComponent.NodeComponent):
    type = dnConstants.COMP_USER_APP
    name = u'Timber connection EN 1995'
    description = trans(u'Designing timber dowel type fasteners connection')
    dirPath = os.path.join(dnConstants.LIB_DIR_PATH, 'components/node/PolaczenieDrewniane/')
    iconPath = os.path.join(dnConstants.LIB_DIR_PATH, 'components/node/PolaczenieDrewniane/img/icon.gif')
    summarySubjects = [
        final_capacity_ratio
    ]

    def __init__(self, parent, itemid):

        dnComponent.NodeComponent.__init__(self, parent, itemid)

        #self.setDefault()

    def setDefault(self):

        #metoda obiektu nedrzednego
        dnComponent.NodeComponent.setDefault(self)

        elements = self.getItem().getElements(node='both')
        def_designed_id = elements[0].getNumber()
        def_other_id = elements[1].getNumber()
        #class vars

        self.forces_chb = 0
        # self.forces_ignore_sign = 0
        self.connect_to_radio = 0
        self.nail_radio = 'Round Nails'
        self.predrilled_holes = 1
        self.calc_bend_tens = 1

        self.designed_id_str = def_designed_id
        self.other_id_str = def_other_id

        self.gamma_m = 1.3
        self.k_mod = 0.80
        self.calc_axially_loaded = 0
        self.f_ax_ed = 0

        self.diameter = 6
        self.num_of_fasteners = 2
        self.num_of_rows = 1
        self.nail_length = 900
        self.two_sided = 0
        self.a1 = 30
        self.a2 = 18
        self.theta = 45
        self.f_u = 600

        self.bolt_str = '5.8'
        self.boltd_str = 'M10'

        self.l_control = 500
        self.axial_f = 0
        self.shear_f = 0
        self.bending_m = 0

        self.force_plate_inside = 0
        self.plate_l = 200
        self.plate_h = elements[0].getComplexProfile().get_H() / 2
        self.plate_t = 3
        self.plate_delta = 0

    def doCustomCheck(self):

        self.designed_id = int(self.designed_id_str)
        self.other_id = int(self.other_id_str)
        if self.num_of_fasteners * self.num_of_rows < 2:
            self.getMessageManager().addMessage(u'At least 2 fasteners are required', type=dnComponent.MSG_TYPE_ERROR)
            return False
        if self.designed_id == self.other_id and self.connect_to_radio == 0:
            self.getMessageManager().addMessage(u'Same designed/other bar id!', type=dnComponent.MSG_TYPE_ERROR)
            return False
        return True

    def doBeforeCalculate(self):

        self.nail_type_str = self.nail_radio
        self.connection_type_str = ''

        if self.nail_type_str == 'Bolts':
            bolt_strength = {'4.6': [240., 400.], '4.8': [340., 420.], '5.6': [300., 500.], '5.8': [420., 520.],
                             '6.8': [480., 600.], '8.8': [640., 800.], '10.9': [900., 1000.]}
            self.f_u = bolt_strength[self.bolt_str][0]
            self.d = int(self.boltd_str[1:])
        else:
            self.d = self.diameter
        if self.connect_to_radio == 0:
            self.connect_with_other_element = True
        else:
            self.connect_with_other_element = False

        return True

    def doCalculate(self, soft=False):

        plate_thickness = 0
        timber_ele_id = 99
        node_object = self.getItem()
        node_number = node_object.getNumber()
        elements = node_object.getElements(node='both')

        #angles dict (true angles for swapped nodes elements)
        angles_dict = {}
        for p in elements:
            if p.getNodesNums()[0] != node_number:
                angles_dict[p.getNumber()] = p.getAngle() + pi
            else:
                angles_dict[p.getNumber()] = p.getAngle()
        for p in angles_dict:
            if round(angles_dict[p] - 2 * pi) > -0.01:
                angles_dict[p] -= 2 * pi

        # Determining pairs
        paired = []
        checked = []
        for e_obj in elements:
            for e_to_check_obj in elements:
                if e_to_check_obj != e_obj and e_to_check_obj not in checked:

                    e1_obj, e2_obj = e_obj, e_to_check_obj

                    e1_n1, e1_n2 = e1_obj.getNodes()
                    e2_n1, e2_n2 = e2_obj.getNodes()
                    e1_start_from_node = node_object == e1_n1
                    e2_start_from_node = node_object == e2_n1
                    if e1_start_from_node != e2_start_from_node and \
                                    fabs(e1_obj.getAngle() - e2_obj.getAngle()) < 2. / 180. * pi or \
                                            e1_start_from_node == e2_start_from_node and \
                                            fabs(fabs(e1_obj.getAngle() - e2_obj.getAngle()) - pi) < 2. / 180. * pi:
                        paired.append([e1_obj, e2_obj])

            checked.append(e_obj)
        # Determining unpaired bars
        for p in paired:
            if p[0] in checked:
                checked.remove(p[0])
            if p[1] in checked:
                checked.remove(p[1])
        # checked is left with unpaired bars only

        # Invade check
        paired_ids = []
        for p in paired:
            paired_ids.append(p[0].getNumber())
            paired_ids.append(p[1].getNumber())

        for p in paired_ids:
            if paired_ids.count(p) > 1:
                self.getMessageManager().addMessage(u'Bars invade each other!', type=dnComponent.MSG_TYPE_ERROR)
                return False

        # Locate designed elements on list
        all_ids = []
        for p in elements:
            all_ids.append(p.getNumber())
            if p.getNumber() == self.designed_id:
                ele_0 = p
            if p.getNumber() == self.other_id:
                ele_1 = p

        # ele 0 - designed, ele 1 - other

        # connection with other bar
        if self.connect_with_other_element:

            # Section check, fitting in 2 shear planes, t1, t2
            principal_elements = [ele_0, ele_1]
            complex_profiles = [principal_elements[0].getComplexProfile(), principal_elements[1].getComplexProfile()]
            profiles = [complex_profiles[0].getProfiles(), complex_profiles[1].getProfiles()]
            profiles_count = [len(profiles[0]), len(profiles[1])]

            shear_planes = 1
            two_profiles_element_id = []
            one_profile_element_id = []

            steel_plate_inside = []

            # identify bar with two profiles
            if profiles_count[0] > 1:
                shear_planes = 2
                two_profiles_element_id = 0
                one_profile_element_id = 1

            if profiles_count[1] > 1:
                shear_planes = 2
                if two_profiles_element_id == 0:
                    self.getMessageManager().addMessage(u'Both intersecting sections have two profiles!',
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    return False
                two_profiles_element_id = 1
                one_profile_element_id = 0

            # set thickness
            if shear_planes == 1:
                t1 = complex_profiles[0].get_S()
                t2 = complex_profiles[1].get_S()
                thickness = [t1, t2]

            else:
                two_profiles_element = complex_profiles[two_profiles_element_id]
                two_prof_ele_overall_thickness = two_profiles_element.get_S()
                sections = [two_profiles_element.getProfiles()[0].getSection(),
                            two_profiles_element.getProfiles()[1].getSection()]
                branches_widths = [sections[0].get_B(),
                                   sections[1].get_B()]
                if branches_widths[0] != branches_widths[1]:
                    self.getMessageManager().addMessage(u"Branches are different!",
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    return False

                prof_inside_ele_width = complex_profiles[one_profile_element_id].get_S()

                t1 = branches_widths[0]
                t2 = prof_inside_ele_width

                thickness = [t1, t2]

        # connection with steel plate
        else:
            complex_profiles = [ele_0.getComplexProfile()]
            profiles_count = [len(complex_profiles[0].getProfiles())]
            shear_planes = 2
            plate_thickness = self.plate_t

            if profiles_count[0] == 1:  # steel plate outside

                two_prof_ele_overall_thickness = complex_profiles[0].get_S() + 2 * plate_thickness
                branches_widths = [plate_thickness]  # treat plate as 2 branch element
                prof_inside_ele_width = complex_profiles[0].get_S()

                steel_plate_inside = False
                t1 = plate_thickness
                t2 = prof_inside_ele_width

                two_profiles_element_id = 1
                one_profile_element_id = 0

            if profiles_count[0] == 2:  # steel plate inside
                two_prof_ele_overall_thickness = complex_profiles[0].get_S()  # thickness with space between
                branches_widths = [complex_profiles[0].getProfiles()[0].getSection().get_B(),
                                   complex_profiles[0].getProfiles()[1].getSection().get_B()]
                if branches_widths[0] != branches_widths[1]:
                    self.getMessageManager().addMessage(u"Branches are different!",
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    return False

                plate_thickness = two_prof_ele_overall_thickness - 2 * branches_widths[0]  # suggested plate_t, to fill
                prof_inside_ele_width = plate_thickness

                steel_plate_inside = True
                t1 = branches_widths[0]
                t2 = prof_inside_ele_width

                two_profiles_element_id = 0
                one_profile_element_id = 1

            if self.force_plate_inside == 1:
                two_prof_ele_overall_thickness = complex_profiles[0].get_S()
                branches_widths = [(two_prof_ele_overall_thickness - plate_thickness) / 2]  # wytnij blaszke w elemencie
                prof_inside_ele_width = plate_thickness

                t1 = branches_widths[0]
                t2 = prof_inside_ele_width

                two_profiles_element_id = 0
                one_profile_element_id = 1

            thickness = [t1, t2]

        # common part, space check
        if shear_planes == 2:

            space_between = two_prof_ele_overall_thickness - 2 * branches_widths[0] - prof_inside_ele_width
            if space_between < 0:
                self.getMessageManager().addMessage(u"Profiles don't fit into each other (too little space)",
                                                    type=dnComponent.MSG_TYPE_ERROR)
                #return False
            if space_between > 10:
                self.getMessageManager().addMessage(u"Profiles don't fit into each other (too large space)",
                                                    type=dnComponent.MSG_TYPE_ERROR)
                return False
        for pc in profiles_count:
            if pc > 2:
                self.getMessageManager().addMessage(u'One bar consists of more than 2 branches',
                                                    type=dnComponent.MSG_TYPE_ERROR)
                return False

        # material, density, shear forces for splitting check
        node_stat_result_obj = node_object.getResults().getStatResults()
        if self.connect_with_other_element:
            materials = [complex_profiles[0].getPrincipalMaterial(), complex_profiles[1].getPrincipalMaterial()]
            mat_types = [materials[0].getType(), materials[1].getType()]
            mat_names = [materials[0].getName()[:1], materials[1].getName()[:1]]
            if 'Stal' in mat_types:
                if mat_types.count('Stal') > 1:
                    self.getMessageManager().addMessage(u"Both elements are steel elements!",
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    return False
                steel_in_connection = True
                steel_ele_id = mat_types.index('Stal')
                timber_ele_id = abs(steel_ele_id - 1)
                timber_type = mat_names[timber_ele_id]
            else:
                steel_in_connection = False
                steel_ele_id = 99
                timber_type = mat_names[0]

            ro = [materials[0].get_ro(), materials[1].get_ro()]

            # other element pair
            other_direction_elements = [ele_1]
            i = 0
            for p in paired:
                if principal_elements[1] in p:
                    pair = i
                    other_direction_elements = paired[pair]
                i += 1
            ot_dir_ele_ids, ot_dir_ele_mat, ot_dir_ele_sec_forces, shear_forces, ot_dir_ele_angles = [], [], [], [], []
            for i in range(0, len(other_direction_elements)):
                ot_dir_ele_angles.append(angles_dict[other_direction_elements[i].getNumber()])
                ot_dir_ele_ids.append(other_direction_elements[i].getId())
                ot_dir_ele_mat.append(other_direction_elements[i].getComplexProfile().getPrincipalMaterial().getType())
                ot_dir_ele_sec_forces. \
                    append(node_stat_result_obj.getSectionForces(ot_dir_ele_ids[i],
                                                                 loadCombination=True,
                                                                 leadingValue=1,
                                                                 laodCombinationType='LOAD_COMB_TYPE_USL_BASIC'))
                shear_forces.append(ot_dir_ele_sec_forces[0].getShearForce())

            if len(ot_dir_ele_ids) == 2:
                if self.other_id == other_direction_elements[1].getNumber():
                    other_element_num = other_direction_elements[0].getNumber()
                else:
                    other_element_num = other_direction_elements[1].getNumber()
            elif len(ot_dir_ele_ids) == 1:
                other_element_num = other_direction_elements[0].getNumber()
            else:
                self.getMessageManager().addMessage(u"Other bar is paired with 2 or more elements. (1 allowed)",
                                                    type=dnComponent.MSG_TYPE_WARNING)

            # angle to grain
            angles = []
            for i in range(0, len(other_direction_elements)):
                angles.append(angles_dict[principal_elements[0].getNumber()] - ot_dir_ele_angles[i])

            ele_angle_to_grain = min(angles, key=abs)
            if ele_angle_to_grain > 2 * pi:
                ele_angle_to_grain -= 2 * pi
            elif ele_angle_to_grain > pi:
                ele_angle_to_grain -= pi
            elif -2 * pi > ele_angle_to_grain:
                ele_angle_to_grain += 2 * pi
            elif -pi > ele_angle_to_grain:
                ele_angle_to_grain += pi

        else:
            # connection with steel plate
            materials = [complex_profiles[0].getPrincipalMaterial()]
            mat_types = [materials[0].getType()]
            mat_names = [materials[0].getName()[:1]]
            timber_type = mat_names[0]
            steel_in_connection = True
            timber_ele_id = 0
            steel_ele_id = 1
            other_element_num = None
            ro = [materials[0].get_ro(), 7860]
            ele_angle_to_grain = 0
            if 'Stal' in mat_types:
                self.getMessageManager().addMessage(u"Both elements are steel elements!",
                                                    type=dnComponent.MSG_TYPE_ERROR)
                return False

        # Fasteners spacing
        # Get dimensions 0 = designed, 1 = other
        h0 = complex_profiles[0].get_H()  # mm
        if self.connect_with_other_element:
            h1 = complex_profiles[1].get_H()  # mm
            angle_between_elements = abs(angles_dict[self.other_id] - angles_dict[self.designed_id])
            if angle_between_elements > pi:
                angle_between_elements = 2 * pi - angle_between_elements

            if abs(ele_angle_to_grain) < radians(20) or abs(ele_angle_to_grain - pi) < radians(20):
                h_0_projection = min(h0, h1)
                h_1_projection = self.l_control
                self.flat_connection = True
            else:
                h_0_projection = h0 / sin(angle_between_elements)
                h_1_projection = h1 / sin(angle_between_elements)
                self.flat_connection = False
        else:
            h1 = self.plate_h
            h_0_projection = min(h0, h1)
            if h1 > h0:
                self.getMessageManager().addMessage(u"Steel plate is wider than timber element. Connection area is now "
                                                    u" limited to timber element width.",
                                                    type=dnComponent.MSG_TYPE_IMPORTANT)
            h_1_projection = self.plate_l
            self.flat_connection = True
        # distances
        parallel_to_end = h_1_projection - (self.num_of_fasteners - 1) * self.a1
        perpendicular_to_end = h_0_projection - (self.num_of_rows - 1) * self.a2

        # loaded/unloaded edges
        if self.forces_chb == 1:
            axial_force = self.axial_f
            shear_force = self.shear_f
            bending_moment = self.bending_m
        else:
            axial_forceli = []
            shear_forceli = []
            bending_momentli = []
            for env_type in ['min', 'max']:
                axial_forceli.append(node_stat_result_obj.
                                     getSectionForces(ele_0.getGraphId(), loadCombination=True, envelopeType=env_type,
                                                      leadingValue=0,
                                                      laodCombinationType='LOAD_COMB_TYPE_USL_BASIC').
                                     getNormalForce() * 1000)
                shear_forceli.append(node_stat_result_obj.
                                     getSectionForces(ele_0.getGraphId(), loadCombination=True, envelopeType=env_type,
                                                      leadingValue=1,
                                                      laodCombinationType='LOAD_COMB_TYPE_USL_BASIC').
                                     getShearForce() * 1000)
                bending_momentli.append(node_stat_result_obj.
                                        getSectionForces(ele_0.getGraphId(), loadCombination=True, leadingValue=2,
                                                         envelopeType=env_type,
                                                         laodCombinationType='LOAD_COMB_TYPE_USL_BASIC').
                                        getBendingMoment() * 1000 * 1000)
            axial_force = max(axial_forceli, key=abs)
            shear_force = max(shear_forceli, key=abs)
            bending_moment = max(bending_momentli, key=abs)

        if axial_force < 0:
            compression = True
        else:
            compression = False

        # overlapping/two sided, nail lenght check
        if self.two_sided == 1:
            if shear_planes == 1:
                self.getMessageManager().addMessage(u"Double sided connectors are not allowed"
                                                    u"in single shear connection", type=dnComponent.MSG_TYPE_ERROR)
                return False
            else:
                if not self.nail_type_str == 'Bolts':
                    if self.nail_length > two_prof_ele_overall_thickness / 2:
                        self.overlapping_nails = 1
                        self.getMessageManager().addMessage(u'Connectors are overlapping',
                                                            type=dnComponent.MSG_TYPE_INFO)
                    else:
                        self.overlapping_nails = 0
        else:
            self.overlapping_nails = 0
        if shear_planes == 1:
            max_nail_length = sum(thickness)
        else:
            max_nail_length = two_prof_ele_overall_thickness
        if max_nail_length < self.nail_length:
            self.getMessageManager().addMessage(u"Nail is longer than connection width "
                                                u"(max." + str(max_nail_length) + u") !",
                                                type=dnComponent.MSG_TYPE_ERROR)

        # capacity modifier (for use in double sided nails & in stapled connections)
        capacity_modifier = 1
        penetration_limit = 0
        k_ef = 1

        if compression:
            des_reaction_angle = 0
            oth_reaction_angle = ele_angle_to_grain
        else:
            des_reaction_angle = 0
            oth_reaction_angle = ele_angle_to_grain

        #
        # 8.3 NAILED CONNECTIONS, 8.7 SCREWED d <= 6 mm
        #

        if (self.nail_type_str == 'Round Nails') or (self.nail_type_str == 'Square/Grooved Nails') or \
                (self.nail_type_str == 'Screws' and self.d <= 6):

            # 8.3.1.1 (1) Thickness, overlapping (fig 8.4)
            if self.two_sided == 0:
                if shear_planes == 1:
                    pointside_penetration = self.nail_length - t1
                    t2 = pointside_penetration
                elif shear_planes == 2:
                    pointside_penetration = self.nail_length - t1 - t2
                    t1 = pointside_penetration

            # 8.3.1.1 (7) (fig 8.5) two sided nails, overlapping
            else:
                if shear_planes == 2:
                    if self.overlapping_nails == 0:
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                    else:
                        t_check = t2
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                        if (t_check - t2) <= 4 * self.d:
                            self.getMessageManager().addMessage(u"Space between nail end and central element end"
                                                                u" is less than 4d. Nail length should be less than " +
                                                                str(t1 + t_check - 4 * self.d) + u" mm",
                                                                type=dnComponent.MSG_TYPE_ERROR)
                        if self.nail_type_str == 'Screws':
                            self.getMessageManager().addMessage(u"Overlapping is not allowed in screwed connections",
                                                                type=dnComponent.MSG_TYPE_ERROR)
                            return False
                    shear_planes = 1
                    capacity_modifier = 2

            # 8.3.1.2 (1) penetration check
            if self.nail_type_str == 'Round Nails':
                penetration_limit = 8 * self.d
            elif self.nail_type_str == 'Square/Grooved Nails' or self.nail_type_str == 'Screws':
                penetration_limit = 6 * self.d

            # 8.3.1.2 (5) Minimum spacings, end distances, k_e, n_ef
            def calc_a_lim(alfa_c, d_c, holes, ro_c):
                if holes:
                    a1_c_lim = (4 + abs(cos(alfa_c))) * d_c
                    a2_c_lim = (3 + abs(sin(alfa_c))) * d_c
                    a3c_c_lim = 7 * d_c
                    a3t_c_lim = (7 + 5 * cos(alfa_c)) * d_c
                    a4c_c_lim = 3 * d_c
                    if d_c >= 5:
                        a4t_c_lim = (3 + 4 * sin(alfa_c)) * d_c
                    else:
                        a4t_c_lim = (3 + 2 * sin(alfa_c)) * d_c
                else:
                    if (ro_c[0] <= 420) or (ro_c[1] <= 420):
                        if d_c >= 5:
                            a1_c_lim = (5 + 7 * abs(cos(alfa_c))) * d_c
                        else:
                            a1_c_lim = (5 + 5 * abs(cos(alfa_c))) * d_c
                        a2_c_lim = 5 * d_c
                        a3t_c_lim = (10 + 5 * cos(alfa_c)) * d_c
                        a3c_c_lim = 10 * d_c
                        if d_c >= 5:
                            a4t_c_lim = (5 + 5 * sin(alfa_c)) * d_c
                        else:
                            a4t_c_lim = (5 + 2 * sin(alfa_c)) * d_c
                        a4c_c_lim = 5 * d_c
                    elif (ro_c[0] <= 500) or (ro_c[1] <= 500):
                        a1_c_lim = (7 + 8 * abs(cos(alfa_c))) * d_c
                        a2_c_lim = 7 * d_c
                        a3t_c_lim = (15 + 5 * cos(alfa_c)) * d_c
                        a3c_c_lim = 15 * d_c
                        if d_c >= 5:
                            a4t_c_lim = (7 + 2 * sin(alfa_c)) * d_c
                        else:
                            a4t_c_lim = (7 + 5 * sin(alfa_c)) * d_c
                        a4c_c_lim = 7 * d_c
                    else:
                        self.getMessageManager().addMessage(u"Connections with timber of density above 500 kg/m^3"
                                                            u" should have predrilled holes",
                                                            type=dnComponent.MSG_TYPE_ERROR)
                        return False
                        # [0] a1_c_lim , [1] a2_c_lim,
                        # [2] a3t_c_lim, [3] a3c_c_lim,
                        # [4] a4t_c_lim, [5] a4c_c_lim
                return [a1_c_lim, a2_c_lim, a3t_c_lim, a3c_c_lim, a4t_c_lim, a4c_c_lim]

            a_lims_des = calc_a_lim(des_reaction_angle, self.d, self.predrilled_holes, ro)
            a_lims_other = calc_a_lim(oth_reaction_angle, self.d, self.predrilled_holes, ro)

            if self.flat_connection:
                a3t = a_lims_des[2]
                a3c = a_lims_des[3]
                a4t = a_lims_des[4]
                a4c = a_lims_des[5]
            else:
                a3t = max(a_lims_des[2], a_lims_other[4])
                a3c = max(a_lims_des[3], a_lims_other[5])
                a4t = max(a_lims_des[4], a_lims_other[2])
                a4c = max(a_lims_des[5], a_lims_other[3])

            a_str = ['a1', 'a2', 'a3t', 'a3c', 'a4t', 'a4c']
            a_user = [self.a1, self.a2, parallel_to_end / 2, parallel_to_end / 2, perpendicular_to_end / 2,
                      perpendicular_to_end / 2]
            if steel_in_connection:
                a_lims = [0.7 * a_lims_des[0], 0.7 * a_lims_des[1], a3t, a3c, a4t, a4c]
            else:
                a_lims = [a_lims_des[0], a_lims_des[1], a3t, a3c, a4t, a4c]

            if self.predrilled_holes:
                a1_ranges = [0, 4 * self.d, 7 * self.d, 10 * self.d, 14 * self.d]
                ke_values = [0.5, 0.5, 0.7, 0.85, 1]
            else:
                a1_ranges = [4 * self.d, 7 * self.d, 10 * self.d, 14 * self.d]
                ke_values = [0, 0.7, 0.85, 1]
            if self.a1 in a1_ranges:
                k_ef = ke_values[a1_ranges.index(self.a1)]
            else:
                higher = 0
                lower = 0
                i = 0
                for ran in a1_ranges:
                    if self.a1 < ran:
                        if higher == 0:
                            higher = i
                    if self.a1 > ran:
                        lower = i
                    i += 1
                k_ef = max(min(ke_values[lower] +
                               (ke_values[higher] - ke_values[lower]) * (self.a1 - a1_ranges[lower])
                               / (a1_ranges[higher] - a1_ranges[lower]), 1), 0)

            n_ef = self.num_of_fasteners ** k_ef

            # 8.3.1.1 (4) m_yrk
            # f_u = tensile strength of the wire in N/mm

            if self.nail_type_str == 'Round Nails':
                m_yrk = 0.3 * self.f_u * self.d ** 2.6
            else:
                m_yrk = 0.45 * self.f_u * self.d ** 2.6

        #
        # END OF NAILED CONNECTIONS
        #

        #
        # 8.4 STAPLED CONNECTIONS
        #

        if (self.nail_type_str == 'Round Staples') or (self.nail_type_str == 'Square Staples'):
            if self.nail_type_str == 'Square Staples':
                self.getMessageManager().addMessage(u"For staples with rectangular cross-sections, the diameter d shoul"
                                                    u"d be taken as the square root of the product of both dimensions.",
                                                    type=dnComponent.MSG_TYPE_INFO)
            # 8.3.1.1 (1) Thickness, overlapping (fig 8.4)
            if self.two_sided == 0:
                if shear_planes == 1:
                    pointside_penetration = self.nail_length - t1
                    t2 = pointside_penetration
                elif shear_planes == 2:
                    pointside_penetration = self.nail_length - t1 - t2
                    t1 = pointside_penetration

            # 8.3.1.1 (7) (fig 8.5) two sided nails, overlapping
            else:
                if shear_planes == 2:
                    if self.overlapping_nails == 0:
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                    else:
                        t_check = t2
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                        if (t_check - t2) <= 4 * self.d:
                            self.getMessageManager().addMessage(u"Space between staple end and penetrated element end"
                                                                u" is less than 4d", type=dnComponent.MSG_TYPE_ERROR)
                            return False
                    shear_planes = 1
                    capacity_modifier = 2

            # 8.4 (3) penetration check
            penetration_limit = 14 * self.d

            # 8.3.1.2 (5) Minimum spacings, end distances
            def calc_a_lim(alfa_c, d_c):
                if self.theta >= 30:
                    a1_c_lim = (10 + 5 * abs(cos(alfa_c))) * d_c
                else:
                    a1_c_lim = (15 + 5 * abs(cos(alfa_c))) * d_c
                a2_c_lim = 15 * d_c
                a3t_c_lim = (15 + 5 * abs(cos(alfa_c))) * d_c
                a3c_c_lim = 15 * d_c
                a4t_c_lim = (15 + 5 * abs(sin(alfa_c))) * d_c
                a4c_c_lim = 10 * d_c
                return [a1_c_lim, a2_c_lim, a3t_c_lim, a3c_c_lim, a4t_c_lim, a4c_c_lim]

            a_lims_des = calc_a_lim(des_reaction_angle, self.d)
            a_lims_other = calc_a_lim(oth_reaction_angle, self.d)

            if self.flat_connection:
                a3t = a_lims_des[2]
                a3c = a_lims_des[3]
                a4t = a_lims_des[4]
                a4c = a_lims_des[5]
            else:
                a3t = max(a_lims_des[2], a_lims_other[4])
                a3c = max(a_lims_des[3], a_lims_other[5])
                a4t = max(a_lims_des[4], a_lims_other[2])
                a4c = max(a_lims_des[5], a_lims_other[3])

            a_str = ['a1', 'a2', 'a3t', 'a3c', 'a4t', 'a4c']
            a_user = [self.a1, self.a2, parallel_to_end / 2, parallel_to_end / 2, perpendicular_to_end / 2,
                      perpendicular_to_end / 2]
            a_lims = [a_lims_des[0], a_lims_des[1], a3t, a3c, a4t, a4c]

            a1_ranges = [4 * self.d, 7 * self.d, 10 * self.d, 14 * self.d]
            ke_values = [0, 0.7, 0.85, 1]
            if self.a1 in a1_ranges:
                k_ef = ke_values[a1_ranges.index(self.a1)]
            else:
                higher = 0
                lower = 0
                i = 0
                for ran in a1_ranges:
                    if self.a1 < ran:
                        if higher == 0:
                            higher = i
                    if self.a1 > ran:
                        lower = i
                    i += 1
                k_ef = max(min(ke_values[lower] + (ke_values[higher] - ke_values[lower]) *
                                                  (self.a1 - a1_ranges[lower]) / (a1_ranges[higher] - a1_ranges[lower]),
                               1), 0)

            n_ef = self.num_of_fasteners ** k_ef

            # 8.3.1.1 (4) m_yrk
            # tensile strength of the wire in N/mm
            if self.f_u < 800:
                self.f_u = 800

            m_yrk = 240 * self.d ** 2.6

            # Theta check
            if self.theta < 30:
                capacity_modifier *= 1.4
                self.getMessageManager().addMessage(u"Staples capacity is reduced by 70%"
                                                    u" due to theta<30", type=dnComponent.MSG_TYPE_INFO)
            else:
                capacity_modifier *= 2

        #
        # END OF STAPLED CONNECTIONS
        #

        #
        # 8.5 BOLTED CONNECTIONS, 8.7 SCREWED CONNECTIONS d > 6 mm
        #

        if self.nail_type_str == 'Bolts' or (self.nail_type_str == 'Screws' and self.d > 6):
            if not 6 <= self.d <= 30:
                self.getMessageManager().addMessage(u"Outside 6 mm < d < 30 mm range",
                                                    type=dnComponent.MSG_TYPE_ERROR)
                return False

            # 8.3.1.1 (1) Thickness, overlapping for screws
            if self.nail_type_str == 'Screws':
                if self.two_sided == 0:
                    if shear_planes == 1:
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                    elif shear_planes == 2:
                        pointside_penetration = self.nail_length - t1 - t2
                        t1 = pointside_penetration

                # 8.3.1.1 (7) (fig 8.5) two sided screws, overlapping
                else:
                    if shear_planes == 2:
                        if self.overlapping_nails == 0:
                            pointside_penetration = self.nail_length - t1
                            t2 = pointside_penetration
                        else:
                            self.getMessageManager().addMessage(u"Screws can't overlap",
                                                                type=dnComponent.MSG_TYPE_ERROR)
                            return False
                        shear_planes = 1
                        capacity_modifier = 2

                # penetration
                penetration_limit = 6 * self.d

            # overlapping for bolts, two sided bolts
            if self.nail_type_str == 'Bolts':
                # penetration check (no pen)
                pointside_penetration = 0
                penetration_limit = 0
                if shear_planes == 1:
                    self.nail_length = floor(sum(thickness))
                    self.getMessageManager().addMessage('Bolt length adjusted to connection width ('
                                                        + str(self.nail_length) + ' mm)',
                                                        type=dnComponent.MSG_TYPE_INFO)
                else:
                    self.nail_length = floor(two_prof_ele_overall_thickness)
                    self.getMessageManager().addMessage('Bolt length adjusted to connection width ('
                                                        + str(self.nail_length) + ' mm)',
                                                        type=dnComponent.MSG_TYPE_INFO)

            # 8.3.1.2 (5) Minimum spacings, end distances, k_e, n_ef
            def calc_a_lim(alfa_c, d_c):
                a1_c_lim = (4 + abs(cos(alfa_c))) * d_c
                a2_c_lim = 4 * d_c
                a3t_c_lim = max(7 * d_c, 80)
                a3c_c_lim = max((1 + 6 * sin(alfa_c)) * d_c, 4 * d_c)
                a4c_c_lim = 3 * d_c
                a4t_c_lim = max((2 + 2 * sin(alfa_c)) * d_c, 3 * d_c)
                return [a1_c_lim, a2_c_lim, a3t_c_lim, a3c_c_lim, a4t_c_lim, a4c_c_lim]

            a_lims_des = calc_a_lim(des_reaction_angle, self.d)
            a_lims_other = calc_a_lim(oth_reaction_angle, self.d)

            if self.flat_connection:
                a3t = a_lims_des[2]
                a3c = a_lims_des[3]
                a4t = a_lims_des[4]
                a4c = a_lims_des[5]
            else:
                a3t = max(a_lims_des[2], a_lims_other[4])
                a3c = max(a_lims_des[3], a_lims_other[5])
                a4t = max(a_lims_des[4], a_lims_other[2])
                a4c = max(a_lims_des[5], a_lims_other[3])

            a_str = ['a1', 'a2', 'a3t', 'a3c', 'a4t', 'a4c']
            a_user = [self.a1, self.a2, parallel_to_end / 2, parallel_to_end / 2, perpendicular_to_end / 2,
                      perpendicular_to_end / 2]
            if steel_in_connection:
                a_lims = [0.7 * a_lims_des[0], 0.7 * a_lims_des[1], a3t, a3c, a4t, a4c]
            else:
                a_lims = [a_lims_des[0], a_lims_des[1], a3t, a3c, a4t, a4c]

            n_ef = min(self.num_of_fasteners, self.num_of_fasteners ** 0.9 * (self.a1 / (13 * self.d)) ** 0.25)

            # 8.3.1.1 (4) m_yrk
            # f_u tensile strength of the wire in N/mm
            m_yrk = 0.3 * self.f_u * self.d ** 2.6

        #
        # END OF BOLTED CONNECTIONS
        #

        #
        # 8.6 DOWELLED CONNECTIONS
        #

        if self.nail_type_str == 'Dowels':
            # 8.6 (2) 6 < d <30
            if not 6 < self.d < 30:
                self.getMessageManager().addMessage(u"Outside 6 mm < d < 30 mm range",
                                                    type=dnComponent.MSG_TYPE_ERROR)
                return False

            # 8.3.1.1 (1) Thickness, overlapping (fig 8.4)
            if self.two_sided == 0:
                if shear_planes == 1:
                    pointside_penetration = self.nail_length - t1
                    t2 = pointside_penetration
                elif shear_planes == 2:
                    pointside_penetration = self.nail_length - t1 - t2
                    t1 = pointside_penetration

            # 8.3.1.1 (7) (fig 8.5) two sided nails, overlapping
            else:
                if shear_planes == 2:
                    if self.overlapping_nails == 0:
                        pointside_penetration = self.nail_length - t1
                        t2 = pointside_penetration
                    else:
                        self.getMessageManager().addMessage(u"Dowels can't overlap", type=dnComponent.MSG_TYPE_ERROR)
                        return False
                    shear_planes = 1
                    capacity_modifier = 2

            # penetration
            penetration_limit = 6 * self.d

            # 8.6.(3) Minimum spacings, end distances, k_e, n_ef
            def calc_a_lim(alfa_c, d_c):
                a1_c_lim = (3 + 2 * abs(cos(alfa_c))) * d_c
                a2_c_lim = 3 * d_c
                a3t_c_lim = max(7 * d_c, 80)
                a3c_c_lim = max((a3t_c_lim * sin(alfa_c)) * d_c, 3 * d_c)
                a4c_c_lim = 3 * d_c
                a4t_c_lim = max((2 + 2 * sin(alfa_c)) * d_c, 3 * d_c)
                return [a1_c_lim, a2_c_lim, a3t_c_lim, a3c_c_lim, a4t_c_lim, a4c_c_lim]

            a_lims_des = calc_a_lim(des_reaction_angle, self.d)
            a_lims_other = calc_a_lim(oth_reaction_angle, self.d)

            if self.flat_connection:
                a3t = a_lims_des[2]
                a3c = a_lims_des[3]
                a4t = a_lims_des[4]
                a4c = a_lims_des[5]
            else:
                a3t = max(a_lims_des[2], a_lims_other[4])
                a3c = max(a_lims_des[3], a_lims_other[5])
                a4t = max(a_lims_des[4], a_lims_other[2])
                a4c = max(a_lims_des[5], a_lims_other[3])

            a_str = ['a1', 'a2', 'a3t', 'a3c', 'a4t', 'a4c']
            a_user = [self.a1, self.a2, parallel_to_end / 2, parallel_to_end / 2, perpendicular_to_end / 2,
                      perpendicular_to_end / 2]
            if steel_in_connection:
                a_lims = [0.7 * a_lims_des[0], 0.7 * a_lims_des[1], a3t, a3c, a4t, a4c]
            else:
                a_lims = [a_lims_des[0], a_lims_des[1], a3t, a3c, a4t, a4c]

            n_ef = min(self.num_of_fasteners, self.num_of_fasteners ** 0.9 * (self.a1 / (13 * self.d)) ** 0.25)

            # 8.3.1.1 (4) m_yrk
            # tensile strength of the wire in N/mm
            m_yrk = 0.3 * self.f_u * self.d ** 2.6

        #
        # END OF DOWELLED CONNECTIONS
        #

        # if self.flat_connection:
        #     a_lims[4] = a_lims[5]  # There's no loaded edge in flat connection with compression/tension
        for i in range(0, len(a_user)):
            if a_lims[i] > a_user[i]:
                self.getMessageManager().addMessage('Wrong ' + a_str[i] + ' spacement',
                                                    type=dnComponent.MSG_TYPE_IMPORTANT)

        # 8.5.1.1 (2) Characteristic embedment str
        timber_type_dict = {'C': 1.35, 'D': 1.30, 'G': 0.90}
        k90 = timber_type_dict[timber_type] + 0.015 * self.d

        def f_h_k_calc(ro_, diam, nailtyp, holes, k_90, alf_):
            if (nailtyp == 'Round Nails' or nailtyp == 'Square/Grooved Nails'
                or nailtyp == 'Round Staples' or nailtyp == 'Square Staples') \
                    and diam <= 8 and holes == 0:
                f_h_k_ = 0.082 * ro_ * diam ** -0.3
            else:
                f_h_k_ = 0.082 * (1 - 0.01 * diam) * ro_
            f_h_alf_k = f_h_k_ / (k_90 * sin(alf_) ** 2 + cos(alf_) ** 2)
            return f_h_alf_k, f_h_k_

        f_h1k, f_h1unred = f_h_k_calc(ro[0], self.d, self.nail_type_str, self.predrilled_holes, k90, 0)
        f_h2k, f_h2unred = f_h_k_calc(ro[1], self.d, self.nail_type_str, self.predrilled_holes, k90, ele_angle_to_grain)
        fhk_angles = [0, degrees(ele_angle_to_grain)]

        #
        # F_AX_RK 8.3.2 (4) Characteristic axial withdrawal capacity of the fastener
        #

        # constants for nails
        f_axk = 20 * 10 ** -6 * min(ro) ** 2
        f_headk = 70 * 10 ** -6 * min(ro) ** 2
        if self.d <= 3.75:
            d_h = 2.25 * self.d
        else:
            d_h = 2 * self.d

        if self.nail_type_str == 'Square/Grooved Nails' or self.nail_type_str == 'Square Staples':
            f_axrk = min(f_axk * self.d * pointside_penetration, f_headk * d_h ** 2)
            if pointside_penetration < 12 * self.d:
                f_axrk *= ((pointside_penetration / (2 * self.d)) - 3)
        elif self.nail_type_str == 'Round Nails' or self.nail_type_str == 'Round Staples':
            f_axrk = min(f_axk * self.d * pointside_penetration, f_axk * self.d * thickness[0] + f_headk * d_h ** 2)
            if pointside_penetration < 12 * self.d:
                f_axrk *= ((pointside_penetration / (2 * self.d)) - 3)
        elif self.nail_type_str == 'Bolts':
            bolt_strength = {'4.6': [240., 400.], '4.8': [340., 420.], '5.6': [300., 500.], '5.8': [420., 520.],
                             '6.8': [480., 600.], '8.8': [640., 800.], '10.9': [900., 1000.]}
            self.f_u = bolt_strength[self.bolt_str][0]
            bolt_diameter = {'M08': [8., 36.6], 'M10': [10., 58.], 'M12': [12., 84.3], 'M16': [16., 157.],
                             'M20': [20., 245.], 'M22': [22., 303.], 'M24': [24., 353.], 'M27': [27., 459.],
                             'M30': [30., 561.]}
            f_axrk = 0.9 * self.f_u * bolt_diameter[self.boltd_str][1]
        elif self.nail_type_str == 'Screws':
            f_axk = 3.6 * 10 ** -3 * min(ro) ** 1.5
            l_ef = pointside_penetration - 1 * self.d
            if l_ef < 6 * self.d:
                f_axrk = 0
            else:
                f_axrk = n_ef * (pi * self.d * l_ef) ** 0.8 * f_axk
        else:
            f_axrk = 0

        #
        # END OF F_AX_RK
        #

        f_m_d_max = 0
        f_h_d = 0
        f_v_d = 0
        f_d = 0
        angle_to_grain = 0
        f_ed = abs(axial_force)

        #
        # BENDING
        #
        if self.connect_with_other_element:
            coords, x_coord, y_coord, radius_list, radius_sum = calc_connectors_with_displacement(
                self.num_of_fasteners,
                self.a1,
                angles_dict[self.designed_id],
                self.num_of_rows,
                self.a2,
                angles_dict[self.other_id],
                0,
                0)
            delta = 0
        else:
            coords, x_coord, y_coord, radius_list, radius_sum = calc_connectors_with_displacement(
                self.num_of_fasteners,
                self.a1,
                angles_dict[self.designed_id],
                self.num_of_rows,
                self.a2,
                angles_dict[self.designed_id],
                self.plate_delta,
                self.plate_l)
            delta = self.plate_delta
        r_max = max(radius_list)
        #rad dict
        rad_dict = {}
        for i in range(len(radius_list)):
            rad_dict[radius_list[i]] = coords[i]
        x_max, y_max = rad_dict[r_max]

        n_sum = self.num_of_fasteners * self.num_of_rows

        if self.calc_bend_tens == 1:

            def calc_a_lim_bending(ro_w, nailtype, d, holes, leng):
                if nailtype == 'Round Nails' or nailtype == 'Square/Grooved Nails' or nailtype == 'Round Staples' or \
                        nailtype == 'Square Staples' or (nailtype == 'Screws' and leng <= 6 * d):
                    if ro_w[0] <= 420:
                        a_li_under5 = [12, 12, 15, 10, 15, 10]
                        a_li_below5 = [10, 10, 15, 7, 15, 7]
                    else:
                        a_li_under5 = [15, 15, 20, 12, 20, 12]
                        a_li_below5 = [15, 15, 20, 9, 20, 9]
                    if holes == 1:
                        a_li_under5 = [5, 5, 12, 7, 12, 7]
                        a_li_below5 = [5, 5, 12, 5, 12, 5]
                    if d >= 5:
                        a_li = a_li_under5
                    else:
                        a_li = a_li_below5
                    a_li = [x * d for x in a_li]
                elif nailtype == 'Bolts' or nailtype == 'Dowels' or nailtype == 'Screws':
                    a_li = [6 * d, 6 * d, max(7 * d, 80), 4 * d, max(7 * d, 80), 4 * d]
                else:
                    self.getMessageManager().addMessage('Unsupported connector type',
                                                        type=dnComponent.MSG_TYPE_IMPORTANT)
                    return False
                return a_li

            a_lims_ben = calc_a_lim_bending(ro, self.nail_type_str, self.d, self.predrilled_holes, self.nail_length)

            a3t = a_lims_ben[2]
            a3c = a_lims_ben[3]
            a4t = a_lims_ben[4]
            a4c = a_lims_ben[5]

            if steel_in_connection:
                a_lims_b = [0.7 * a_lims_ben[0], 0.7 * a_lims_ben[1], a3t, a3c, a4t, a4c]
            else:
                a_lims_b = [a_lims_ben[0], a_lims_ben[1], a3t, a3c, a4t, a4c]

            for i in range(0, len(a_user)):
                a_lims[i] = max(a_lims[i], a_lims_b[i])
                if a_lims[i] > a_user[i]:
                    self.getMessageManager().addMessage('Wrong ' + a_str[i] + ' spacement',
                                                        type=dnComponent.MSG_TYPE_IMPORTANT)
            f_m_d_max = (bending_moment + shear_force * delta) * r_max / (radius_sum * shear_planes)
            f_h_d = axial_force / (n_sum * shear_planes)
            f_v_d = shear_force / (n_sum * shear_planes)
            f_d = sqrt((f_v_d + f_m_d_max * x_max / r_max) ** 2 + (f_h_d + f_m_d_max * y_max / r_max) ** 2)
            if f_d == 0:
                angle_to_grain = 0
            else:
                angle_to_grain = abs(acos((f_h_d + f_m_d_max * y_max / r_max) / f_d))
            angle_to_other_ele = abs(ele_angle_to_grain + angle_to_grain)

            f_h1k, f_h1unred = f_h_k_calc(ro[0], self.d, self.nail_type_str, self.predrilled_holes, k90,
                                          angle_to_grain)
            f_h2k, f_h2unred = f_h_k_calc(ro[1], self.d, self.nail_type_str, self.predrilled_holes, k90,
                                          angle_to_other_ele)
            fhk_angles = [degrees(angle_to_grain), degrees(angle_to_other_ele)]

        #
        # END OF BENDING
        #

        a3sum = max(a_lims[2], a_lims[3])
        a4sum = max(a_lims[4], a_lims[5])
        parallel_to_end = h_1_projection - (self.num_of_fasteners - 1) * self.a1
        max_num_of_fasteners = max(floor((h_1_projection - 2. * a3sum)/self.a1 + 1.), 2.)
        max_num_of_rows = max(floor((h_0_projection - 2. * a4sum)/self.a2 + 1.), 1.)

        #
        # F_90_check
        #

        f_v_ed = 0
        f_90_rk = 0
        f_90_rd = 0
        b = 0
        h_e = 0
        f_90_ratio = 0

        # connection with other bar
        if self.connect_with_other_element:
            # f_90rd 8.1.4
            if 'Drewno' in ot_dir_ele_mat:
                f_v = []
                for i in range(0, len(other_direction_elements)):
                    f_v.append(abs(shear_forces[i]))  # kN
                    f_v_ed = max(f_v)
                w = 1

                for profile in profiles[1]:  # profiles[1] = other element profiles
                    b += profile.getSection().get_B()
                h_e = parallel_to_end / 2
                if h_e / (1 - h_e / h_1_projection) < 0:
                    f_90_rk = 0
                else:
                    f_90_rk = 14 * b * w * sqrt(h_e / (1 - h_e / h_1_projection)) / 1000  # kN
                f_90_rd = self.k_mod / self.gamma_m * f_90_rk
                if f_v_ed > f_90_rd:
                    self.getMessageManager().addMessage(u"Profile is splitted by tension force component.",
                                                        type=dnComponent.MSG_TYPE_WARNING)
                if f_90_rd <= 0:
                    self.getMessageManager().addMessage(u"Connectors are outside connection area!.",
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    f_90_ratio = 0
                else:
                    f_90_ratio = f_v_ed / f_90_rd

        #
        # END OF F_90_check
        #

        f_h_k_list = [f_h1k, f_h2k]
        f_h_k_unred_list = [f_h1unred, f_h2unred]
        if steel_plate_inside == False:
            penetration_limit = 0
        if pointside_penetration < penetration_limit:
            self.getMessageManager().addMessage(u"Penetration length is too short!", type=dnComponent.MSG_TYPE_ERROR)

        if steel_in_connection:
            f_h_k = f_h_k_list[timber_ele_id]
            t_steel = thickness[steel_ele_id]
            if (self.nail_type_str == 'Round Staples') or (self.nail_type_str == 'Square Staples'):
                self.getMessageManager().addMessage(u"You are about to design connection with staples and metal"
                                                    u" elements!", type=dnComponent.MSG_TYPE_INFO)

        # 8.2.2 (2) Reduction of rope effect contribution to Johansen part
        nails_red_tab = {'Round Nails': 0.15,
                         'Round Staples': 0.15,
                         'Square/Grooved Nails': 0.25,
                         'Square Staples': 0.25,
                         'Bolts': 0.25,
                         'Screws': 1,
                         'Dowels': 0,
                         'Other': 0.5}
        rope_eff_red = nails_red_tab[self.nail_type_str]

        beta = f_h2k / f_h1k

        def timber_single_shear():
            self.connection_type_str = 'Timber to timber connection\n'
            a = f_h1k * t1 * self.d
            b_ = f_h2k * t2 * self.d
            c = f_h1k * t1 * self.d / (1 + beta) * (
                sqrt(beta + 2 * beta ** 2 * (1 + t2 / t1 + (t2 / t1) ** 2) + beta ** 3 * (t2 / t1) ** 2) - beta * (
                    1 + t2 / t1))
            c = c + min(rope_eff_red * c, f_axrk / 4)
            d = 1.05 * f_h1k * t1 * self.d / (2 + beta) * (
                sqrt(2 * beta * (1 + beta) + 4 * beta * (2 + beta) * m_yrk / (f_h1k * self.d * t1 ** 2)) - beta)
            d = d + min(rope_eff_red * d, f_axrk / 4)
            e_ = 1.05 * f_h1k * t2 * self.d / (1 + 2 * beta) * (
                sqrt(2 * beta ** 2 * (1 + beta) + 4 * beta * (1 + 2 * beta) * m_yrk / (f_h1k * self.d * t2 ** 2))
                - beta)
            e_ = e_ + min(rope_eff_red * e_, f_axrk / 4)
            f = 1.15 * sqrt(2 * beta / (1 + beta)) * sqrt(2 * m_yrk * f_h1k * self.d)
            f = f + min(rope_eff_red * f, f_axrk / 4)
            force = {a: 'a', b_: 'b', c: 'c', d: 'd', e_: 'e', f: 'f'}
            return force

        def timber_double_shear():
            self.connection_type_str = 'Timber to timber connection\n'
            g = f_h1k * t1 * self.d
            h_ = 0.5 * f_h2k * t2 * self.d
            j = 1.05 * f_h1k * t1 * self.d / (2 + beta) * (
                sqrt(2 * beta * (1 + beta) + 4 * beta * (2 + beta) * m_yrk / (f_h1k * self.d * t1 ** 2)) - beta)
            j = j + min(rope_eff_red * j, f_axrk / 4)
            k = 1.15 * sqrt(2 * beta / (1 + beta)) * sqrt(2 * m_yrk * f_h1k * self.d)
            k = k + min(rope_eff_red * k, f_axrk / 4)
            force = {g: 'g', h_: 'h', j: 'j', k: 'k'}
            return force

        def steel_single_shear(t_wood):
            self.connection_type_str = 'Timber to steel connection\n'
            a = 0.4 * f_h_k * t_wood * self.d
            b_ = 1.15 * sqrt(2 * m_yrk * f_h_k * self.d)
            b_ = b_ + min(rope_eff_red * b_, f_axrk / 4)

            c = f_h_k * t_wood * self.d
            d = f_h_k * t_wood * self.d * (sqrt(2 + 4 * m_yrk / (f_h_k * self.d * t_wood ** 2)) - 1)
            d = d + min(rope_eff_red * d, f_axrk / 4)
            e_ = 2.3 * sqrt(m_yrk * f_h_k * self.d)
            e_ = e_ + min(rope_eff_red * e_, f_axrk / 4)

            if t_steel <= 0.5 * self.d:
                force = {a: 'a', b_: 'b'}
            elif t_steel > self.d:
                force = {c: 'c', d: 'd', e_: 'e'}
            else:
                force = {
                    a + (c - a) * (t_steel - 0.5 * self.d) / (self.d - 0.5 * self.d): 'a+c',
                    b_ + (e_ - b_) * (t_steel - 0.5 * self.d) / (self.d - 0.5 * self.d): 'b+e'
                }
            return force

        def steel_double_shear_inside():
            self.connection_type_str = 'Timber to steel\nelement inside connection'
            f = f_h_k * t1 * self.d
            g = f_h_k * t1 * self.d * (sqrt(2 + 4 * m_yrk / (f_h_k * self.d * t1 ** 2)) - 1)
            g = g + min(rope_eff_red * g, f_axrk / 4)
            h_ = 2.3 * sqrt(m_yrk * f_h_k * self.d)
            h_ = h_ + min(rope_eff_red * h_, f_axrk / 4)
            force = {f: 'f', g: 'g', h_: 'h'}
            return force

        def steel_double_shear_outside():
            self.connection_type_str = 'Timber to two steel\nelements outside connection'
            j = 0.5 * f_h_k * t2 * self.d
            k = 1.15 * sqrt(2 * m_yrk * f_h_k * self.d)
            k = k + min(rope_eff_red * k, f_axrk / 4)

            l = 0.5 * f_h_k * t2 * self.d
            m = 2.3 * sqrt(2 * m_yrk * f_h_k * self.d)
            m = m + min(rope_eff_red * m, f_axrk / 4)

            if t_steel <= 0.5 * self.d:
                force = {j: 'j', k: 'k'}
            elif t_steel > self.d:
                force = {l: 'l', m: 'm'}
            else:
                force = {
                    j: 'j+l',
                    k + (m - k) * (t_steel - 0.5 * self.d) / (self.d - 0.5 * self.d): 'k+m'
                }
            return force

        if steel_in_connection:
            if shear_planes == 1:
                f_vrk = steel_single_shear(thickness[timber_ele_id])
            else:
                if two_profiles_element_id == steel_ele_id:
                    if self.two_sided == 0 and not self.nail_type_str == 'Bolts':
                        self.getMessageManager().addMessage(u'Single sided connectors are inefficient in such '
                                                            u'connection', type=dnComponent.MSG_TYPE_IMPORTANT)
                    f_vrk = steel_double_shear_outside()
                elif one_profile_element_id == steel_ele_id:
                    if self.two_sided == 1 and not self.nail_type_str == 'Bolts':
                        self.getMessageManager().addMessage(u'Double sided connectors are inefficient in such'
                                                            u' connection', type=dnComponent.MSG_TYPE_IMPORTANT)
                    f_vrk = steel_double_shear_inside()
                else:
                    self.getMessageManager().addMessage(u'Steel element Ids don"t match',
                                                        type=dnComponent.MSG_TYPE_ERROR)
                    return False

        elif shear_planes == 1:
            f_vrk = timber_single_shear()
        else:
            f_vrk = timber_double_shear()

        f_vefrk = n_ef * min(f_vrk) * self.num_of_rows * shear_planes * capacity_modifier
        f_vefrd = self.k_mod * f_vefrk / self.gamma_m
        use_ratio = f_ed / f_vefrd

        if self.calc_bend_tens == 1:
            f_vefrkbend = min(f_vrk) * capacity_modifier
            f_vefrdbend = self.k_mod * f_vefrkbend / self.gamma_m
            use_ratiobend = f_d / f_vefrdbend
            final_ratio = max(use_ratiobend, use_ratio)
        else:
            f_vefrkbend = 0
            f_vefrdbend = 0
            use_ratiobend = 0
            final_ratio = use_ratio
        axial_ratio = 0
        if self.calc_axially_loaded:
            f_axrd = self.k_mod * f_axrk / self.gamma_m
            if self.nail_type_str == 'Nails':
                axial_ratio = (self.f_ax_ed*1000/n_sum) / f_axrd + max(use_ratio, use_ratiobend)
            else:
                axial_ratio = ((self.f_ax_ed*1000/n_sum) / f_axrd)**2 + (max(use_ratio, use_ratiobend))**2
        self.getResults().setResults({
            'a1_lim': a_lims[0],
            'a2_lim': a_lims[1],
            'a3t': a3t,
            'a3c': a3c,
            'a4t': a4t,
            'a4c': a4c,
            'angle_to_grain': degrees(angle_to_grain),
            'axial_force': axial_force,
            'axial_ratio': axial_ratio,
            'bending_moment': bending_moment,
            'beta': beta,
            'coords': coords,
            'connection_type_str': self.connection_type_str,
            'd': self.d,
            'ele_angle_to_grain': degrees(ele_angle_to_grain),
            'flat_connection': self.flat_connection,
            'f_90_ratio': f_90_ratio,
            'f_90_rd': f_90_rd,
            'f_90_rk': f_90_rk,
            'f_axrk': f_axrk,
            'f_d': f_d,
            'f_ed': f_ed,
            'f_h_d': f_h_d,
            'f_h_k_unred_list': f_h_k_unred_list,
            'fhk_angles': fhk_angles,
            'f_h_k_list': f_h_k_list,
            'f_m_d_max': f_m_d_max,
            'f_u': self.f_u,
            'f_v_d': f_v_d,
            'f_v_ed': f_v_ed,
            'f_vefrk': f_vefrk,
            'f_vefrd': f_vefrd,
            'f_vefrkbend': f_vefrkbend,
            'f_vefrdbend': f_vefrdbend,
            'f_vrk': f_vrk,
            'final_capacity_ratio': final_ratio,
            'h_0_projection': h_0_projection,
            'h_1_projection': h_1_projection,
            'k_ef': k_ef,
            'max_nail_length': max_nail_length,
            'max_num_of_rows': max_num_of_rows,
            'max_num_of_fasteners': max_num_of_fasteners,
            'min(f_vrk)': min(f_vrk),
            'myrk': m_yrk,
            'nef': n_ef,
            'other_element_num': other_element_num,
            'parallel_to_end': parallel_to_end / 2,
            'penetration_limit': penetration_limit,
            'perpendicular_to_end': perpendicular_to_end / 2,
            'plate_t': plate_thickness,
            'pointside_penetration': pointside_penetration,
            'r_max': r_max,
            'radius_sum': radius_sum,
            'ro': ro,
            'self.a1': self.a1,
            'self.a2': self.a2,
            'shear_b': b,
            'shear_h_e': h_e,
            'shear_force': shear_force,
            'shear_planes': shear_planes,
            'steel_ele_id': steel_ele_id,
            'steel_in_connection': steel_in_connection,
            'steel_plate_inside': steel_plate_inside,
            't1': t1,
            't2': t2,
            'timber_ele_id': timber_ele_id,
            'two_profiles_element_id': two_profiles_element_id,
            'ratio': use_ratio,
            'ratiobend': use_ratiobend,
            'x_max': x_max,
            'y_max': y_max,

        })
        self.getResults().setSummary(
            [
                ['final_capacity_ratio', final_ratio],
            ]
        )

        return True

    def insertRTFReport(self, doc_obj, section_obj):

        result_obj = self.getResults()
        #utworzenie obiektu z metodami do tworzenia raportu
        rtf_report_method = sdRTFReport.RTFRaport_MethodsObj(self, doc_obj, section_obj)
        #spacer
        # indent = 3 * ' '

        #dodanie naglowka
        self.insertRTFReport_ComponentHeader(rtf_report_method)

        #wstawienie informacji o wezle
        self.insertRTFReport_ItemInfo(rtf_report_method)

        #pobarnie stylu z obiektu dokumentu
        # ss = doc_obj.StyleSheet
        n_sp = result_obj.getResult('shear_planes')
        #zmienne projektowe elementow
        rtf_report_method.insertTitle('Dane projektowe elementow')
        if self.connect_with_other_element is False:
            if self.force_plate_inside:
                oth = 'Steel plate inside the pocket carved in the element'
            else:
                if result_obj.getResult('steel_plate_inside'):
                    oth = 'Steel plate inside two branches element'
                else:
                    oth = 'Two steel plates, joined outside the designed element'
        else:
            oth = self.other_id

        # geom
        self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'geom', {
            'desid': self.designed_id,
            'bear': oth,
            'd': self.d,
            'n': self.num_of_fasteners,
            'nsp': n_sp,
            'a1': self.a1,
            'a2': self.a2,
            'nr': self.num_of_rows,
            'nef': result_obj.getResult('nef'),
            'alfa': result_obj.getResult('ele_angle_to_grain'),
            'a1lim': '%.2f' % result_obj.getResult('a1_lim'),
            'a2lim': '%.2f' % result_obj.getResult('a2_lim'),
            'a3t': '%.2f' % result_obj.getResult('a3t'),
            'a3c': '%.2f' % result_obj.getResult('a3c'),
            'a4t': '%.2f' % result_obj.getResult('a4t'),
            'a4c': '%.2f' % result_obj.getResult('a4c'),
            'apart': '%.2f' % result_obj.getResult('parallel_to_end'),
            'aparc': '%.2f' % result_obj.getResult('parallel_to_end'),
            'apert': '%.2f' % result_obj.getResult('perpendicular_to_end'),
            'aperc': '%.2f' % result_obj.getResult('perpendicular_to_end')

        })

        if self.connect_with_other_element is False:
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'plate', {
                'lplate': self.plate_l,
                'hplate': self.plate_h,
                'tplate': self.plate_t,
                'delplate': self.plate_delta

            })

        # singleshear/doubleshear
        if n_sp == 1:
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'singleshear', {
                't1': result_obj.getResult('t1'),
                't2': result_obj.getResult('t2')
            })
        else:
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'doubleshear', {
                't1': result_obj.getResult('t1'),
                't2': result_obj.getResult('t2')
            })

        # prop
        self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'prop', {
            'ro1': result_obj.getResult('ro')[0],
            'ro2': result_obj.getResult('ro')[1],
            'f_u': self.f_u,
            'gamma_M': self.gamma_m,
            'k_mod': self.k_mod,
            'Ned': '%.0f' % result_obj.getResult('axial_force'),
            'Ved': '%.0f' % result_obj.getResult('shear_force'),
            'Med': '%.0f' % result_obj.getResult('bending_moment')})

        # bending
        if self.calc_bend_tens == 1:
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'bending', {
                'xmax': result_obj.getResult('x_max'),
                'ymax': result_obj.getResult('y_max'),
                'rmax': result_obj.getResult('r_max'),
                'rsum': result_obj.getResult('radius_sum'),
                'nbolt': self.num_of_rows * self.num_of_fasteners,
                'Fmdmax': '%.0f' % result_obj.getResult('f_m_d_max'),
                'Fhd': '%.0f' % result_obj.getResult('f_h_d'),
                'Fvd': '%.0f' % result_obj.getResult('f_v_d'),
                'Fd': '%.0f' % result_obj.getResult('f_d'),
                'alfafddeg': '%.2f' % result_obj.getResult('angle_to_grain'),
            })

        # embedment
        steel_in_conn = result_obj.getResult('steel_in_connection')
        f_h_k_list = result_obj.getResult('f_h_k_list')
        f_h_k_unred_list = result_obj.getResult('f_h_k_unred_list')
        fhk_angles = result_obj.getResult('fhk_angles')
        if steel_in_conn:
            timber_ele_id = result_obj.getResult('timber_ele_id')
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'steel', {
                'fhk': '%.2f' % f_h_k_unred_list[timber_ele_id],
                'alfafhk1': '%.2f' % fhk_angles[timber_ele_id],
                'fh1kalf': '%.2f' % f_h_k_list[timber_ele_id]
            })
        else:
            self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'wood', {
                'fh1k': '%.2f' % f_h_k_unred_list[0],
                'alfafhk1': '%.2f' % fhk_angles[0],
                'fh1kalf': '%.2f' % f_h_k_list[0],
                '2fh2k': '%.2f' % f_h_k_unred_list[1],
                '2alfafhk2': '%.2f' % fhk_angles[1],
                '2fh2kalf': '%.2f' % f_h_k_list[1]
            })
        self.includeExteriorRTF(doc_obj, section_obj, 'main.rtf', 'yield', {
            'myrk': '%.2f' % result_obj.getResult('myrk'),
            'faxrk': '%.2f' % result_obj.getResult('f_axrk'),
        })
        f_vrk_un = result_obj.getResult('f_vrk')
        f_vrk = collections.OrderedDict(sorted(f_vrk_un.items()))
        if steel_in_conn:
            for key in f_vrk.iterkeys():
                if f_vrk[key] == 'a+c':
                    f_vrk[key] = 'qac'
                if f_vrk[key] == 'b+e':
                    f_vrk[key] = 'qbe'
                if f_vrk[key] == 'j+l':
                    f_vrk[key] = 'qjl'
                if f_vrk[key] == 'k+m':
                    f_vrk[key] = 'qkm'
                self.includeExteriorRTF(doc_obj, section_obj, 'steel.rtf', 'key' + f_vrk[key], {
                    'force': '%.0f' % key,
                })

        else:
            for key in f_vrk.iterkeys():
                self.includeExteriorRTF(doc_obj, section_obj, 'timber.rtf', 'key' + f_vrk[key], {
                    'force': '%.0f' % key,
                })
        self.includeExteriorRTF(doc_obj, section_obj, 'fin.rtf', 'capacity', {
            'minfvrk': '%.2f' % result_obj.getResult('min(f_vrk)')})
        if self.calc_bend_tens == 1:
            self.includeExteriorRTF(doc_obj, section_obj, 'fin.rtf', 'bending', {
                'minfvrk': '%.f' % result_obj.getResult('f_vefrkbend'),
                'fvefrdbend': '%.f' % result_obj.getResult('f_vefrdbend'),
                'fed': '%.f' % result_obj.getResult('f_d'),
                'ratiobend': '%.2f' % result_obj.getResult('ratiobend'),
                'fvefrk': '%.f' % result_obj.getResult('f_vefrk'),
                'fvefrd': '%.f' % result_obj.getResult('f_vefrd'),
                'znak': '>',
                'fd': '%.f' % result_obj.getResult('f_ed'),
                'ratio': '%.2f' % result_obj.getResult('ratio')})

        else:
            self.includeExteriorRTF(doc_obj, section_obj, 'fin.rtf', 'comp', {
                'fvefrk': '%.f' % result_obj.getResult('f_vefrk'),
                'fvefrd': '%.f' % result_obj.getResult('f_vefrd'),
                'znak': '>',
                'fd': '%.f' % result_obj.getResult('f_ed'),
                'ratio': '%.2f' % result_obj.getResult('ratio')})

        if result_obj.getResult('f_90_rd') != 0:
            self.includeExteriorRTF(doc_obj, section_obj, 'fin.rtf', 'shear', {
                'b': '%.f' % result_obj.getResult('shear_b'),
                'he': '%.2f' % result_obj.getResult('shear_h_e'),
                'h': '%.f' % result_obj.getResult('h_1_projection'),
                'f90rk': '%.2f' % result_obj.getResult('f_90_rk'),
                'f90rd': '%.2f' % result_obj.getResult('f_90_rd'),
                'shznak': '>',
                'fved': '%.2f' % result_obj.getResult('f_v_ed'),
                'f90ratio': '%.2f' % result_obj.getResult('f_90_ratio')})

    def drawIcon_OFF(self, canvas, x, y):
        #draw symbol
        icon_id = canvas.create_text(
            x,
            y,
            text=soSymbols.greek['Alpha'],
            fill='blue',
            activefill='red',
            font=('symbol', 13, 'bold'),
        )
        return icon_id

    def getDlgClass(self):
        return PolaczenieDrewnianeDlg