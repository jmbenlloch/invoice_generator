import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

import os
import subprocess
import shutil
from glob import glob
from zipfile import ZipFile


def read_template():
    template_file = os.path.join(os.environ['VINCLES'],
                                 'template/plantilla_factura.tex')
    with open(template_file, encoding='utf-8') as fd:
        template = fd.read()
    return template


def replace_params_in_template(template, params):
    for key, value in params.items():
        template = template.replace(f'{{{key}}}', f'{value}')
    return template


def month_to_spanish_name(month):
    meses = ['enero', 'febrero', 'marzo', 'abril',
             'mayo', 'junio', 'julio', 'agosto',
             'septiembre', 'octubre', 'noviembre', 'diciembre']
    return meses[month-1]


def extract_month_and_year(df_visits):
    month = df_visits['Fecha'].apply(lambda x: x.month).mode().values[0]
    year  = df_visits['Fecha'].apply(lambda x: x.year) .mode().values[0]
    return month, year


def parse_visit(row):
    date_parsed = row['Fecha'].strftime('%d/%m/%Y')
    line = '&{} &{} \EURtm \\\\'.format(date_parsed, row['Euros'])
    return line


def process_patient_visits(dni, df_visits, patient, index):
    period_month, period_year = extract_month_and_year(df_visits)

    invoice_date = datetime(period_year, period_month, 1) + timedelta(days=40)
    # TODO  Add sqlite
    invoice_number = f'{period_year}-{period_month:02}-{index:03}'

    padres = patient['Padre/Madre (si menor)']
    nom_factura = padres if isinstance(padres, str) else patient['Nombre']

    visits_parsed = df_visits.sort_values('Fecha').apply(parse_visit, axis=1)
    visits_str = '\n'.join(visits_parsed.values)

    n_sessions = df_visits.shape[0]
    sessions = 'sesiones' if n_sessions > 1 else 'sesión'

    params = {'NOMFACTURA'     : nom_factura,
              'DNI'            : dni,
              'DIRECCIO'       : patient['Direccion'],
              'NUMEROFACTURA'  : invoice_number,
              'NOMPACIENT'     : patient['Nombre'],
              'MES'            : month_to_spanish_name(period_month),
              'ANY'            : period_year,
              'VISITS'         : visits_str,
              'NUMEROSESSIONS' : f'{n_sessions} {sessions}',
              'PREUTOTAL'      : df_visits['Euros'].sum(),
              'MES2'           : month_to_spanish_name(invoice_date.month),
              'ANY2'           : invoice_date.year}

    return params


def generate_invoices(signals, visits_file, patients_file, output_folder):
    # Read data
    df_visits   = pd.read_excel(visits_file)
    df_patients = pd.read_excel(patients_file)

    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Get template
    template = read_template()

    # Create temp dir for latex
    month, year = extract_month_and_year(df_visits)
    temp_fname  = f'{year}_{month:02}'
    temp_dir = os.path.join(output_folder, 'temp', temp_fname)
    os.makedirs(temp_dir, exist_ok=True)

    # Copy latex files to temp dir
    template_files_path = os.path.join(os.environ['VINCLES'], 'template/*png')
    template_files      = glob(template_files_path)
    [shutil.copy(fname, temp_dir) for fname in template_files]

    groups = df_visits.groupby('DNI')

    for i, (dni, group) in enumerate(groups):
        print(dni)

        message = f'Generando factura paciente {dni}'
        signals.progress.emit(message)

        try:
            patient = df_patients[df_patients['DNI'] == dni].iloc[0]
        except IndexError:
            message = f'ERROR: Paciente con {dni} no encontrado'
            signals.error.emit(message)
            continue

        params = process_patient_visits(dni, group, patient, i+1)
        print(params)

        tex_file = replace_params_in_template(template, params)
        fname = f'{dni}.tex'
        fileout = os.path.join(temp_dir, fname)

        with open(fileout, 'w', encoding='utf-8') as fd:
            fd.write(tex_file)

        print(temp_dir.replace('/', '\\'))
        cmd_result = subprocess.run([f"cd {temp_dir}; pdflatex {fname}"], capture_output=True, text=True, shell=True)
        if cmd_result.returncode != 0:
            signals.error.emit(f'Error in file {fileout}')
        print(cmd_result.stdout)
        print(cmd_result.stderr)


    invoices = glob(os.path.join(temp_dir, '*pdf'))
    zip_fname = os.path.join(output_folder, temp_fname + '.zip')

    with ZipFile(zip_fname, 'w') as fd_zip:
        message = f'Generando fichero zip {zip_fname}'
        signals.progress.emit(message)
        for invoice in invoices:
            fd_zip.write(invoice, os.path.basename(invoice))
