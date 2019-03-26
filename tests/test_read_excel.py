import pytest
from convey.io import read_excel


@pytest.fixture
def data_fixture():
    return {
        'filename': 'data/tracking.xlsx',
        'sheetnames': [
            'prints',
            'CT (porosity)',
            'Hardness (Vickers)'
        ],
        'samples': ('G181030a',
                    'G181030b',
                    'G181030c',
                    'G181030d',
                    'G181030e',
                    'G181030f',
                    'G181030g',
                    'G181030h',
                    'G181030i',
                    'M181210a',
                    'MH181210a',
                    'MH181210g'),
        'print columns': ('NAME',
                          'SUBSYSTEM PARENT NAME',
                          'PROPERTY: wire composition',
                          'PROPERTY: wire diameter (mm)',
                          'PROPERTY: wire density (g/cm^3)',
                          'PROPERTY: wire feed rate (mm/s)',
                          'PROPERTY: hot wire setting',
                          'PROPERTY: hot wire power (W)',
                          'PROPERTY: substrate',
                          'PROPERTY: substrate flat',
                          'PROPERTY: substrate level',
                          'PROPERTY: height control',
                          'PROPERTY: substrate thickness (mm)',
                          'PROPERTY: preheat (°C)',
                          'PROPERTY: preheat temperature control',
                          'PROPERTY: laser',
                          'PROPERTY: laser power (W)',
                          'PROPERTY: laser speed (mm/s)',
                          'PROPERTY: laser diameter (mm)',
                          'PROPERTY: laser spot size (mm^2)',
                          'PROPERTY: deposition rate (kg/hr)',
                          'PROPERTY: atmosphere',
                          'PROPERTY: max O2 (ppm)',
                          'PROPERTY: remelt ratio (%)',
                          'PROPERTY: stress relief temperature (°C)',
                          'PROPERTY: stress relief time (hr)',
                          'PROPERTY: bead length (mm)',
                          'PROPERTY: bead cross section (mm^2)',
                          'PROPERTY: bead width (mm)',
                          'PROPERTY: bead height (mm)',
                          'PROPERTY: bead stable'),
        'xct columns': ('NAME',
                        'SUBSYSTEM PARENT NAME',
                        'PROPERTY: Label',
                        'PROPERTY: Volume (µm^3)',
                        'PROPERTY: Sphere Equivalent Diameter (µm)',
                        'PROPERTY: Surface Area (µm^2)',
                        'PROPERTY: Surface Area X (µm^2)',
                        'PROPERTY: Surface Area Y (µm^2)',
                        'PROPERTY: Surface Area Z (µm^2)',
                        'PROPERTY: Volume / Surface Area (µm)',
                        'PROPERTY: Phi (°)',
                        'PROPERTY: Theta (°)',
                        'PROPERTY: Aspect Ratio',
                        'PROPERTY: Center Of Mass X (µm)',
                        'PROPERTY: Center Of Mass Y (µm)',
                        'PROPERTY: Center Of Mass Z (µm)',
                        'PROPERTY: Min Location X (µm)',
                        'PROPERTY: Min Location Y (µm)',
                        'PROPERTY: Min Location Z (µm)',
                        'PROPERTY: Max Location X (µm)',
                        'PROPERTY: Max Location Y (µm)',
                        'PROPERTY: Max Location Z (µm)',
                        'FILE: XCT surface',
                        'FILE: porosity summary powerpoint'),
        'vickers columns': ('NAME',
                            'SUBSYSTEM PARENT NAME',
                            'PROPERTY: Label',
                            'PROPERTY: X-Distance (mm)',
                            'PROPERTY: Vickers Hardness (Hv)',
                            'PROPERTY: Average Values (Hv)'),
        'cells': [
            {'name': 'MH181210a',
             'column': 'PROPERTY: Vickers Hardness (Hv)',
             'value': [[363, 348, 346], [347, 366, 366], [365, 351, 354], [347, 347, 344], [365, 352, 351], [345, 361, 342], [343, 337, 338], [349, 331, 332], [360, 332, 345], [335, 347, 347], [336, 336, 333], [347, 332, 339], [343, 346, 338], [345, 343, 340], [329, 341, 334], [341, 345, 345], [337, 341, 355], [347, 335, 341], [340, 342, 341], [342, 341, 354], [345, 333, 345], [347, 341, 342], [343, 342, 337], [344, 336, 335], [341, 342, 339], [345, 343, 346], [342, 346, 347], [338, 340, 337], [342, 345, 340], [336, 338, 335], [341, 337, 336], [342, 341, 342], [336, 338, 338], [340, 342, 343]]}
        ]
    }


def join(series):
    result = []
    for aseries in series:
        result.extend(list(aseries))
    return result


def test_read_excel(data_fixture):
    dfix = data_fixture
    # ##### expected usage ##### #
    sheets = [read_excel(dfix['filename'], sheetname)
              for sheetname in dfix['sheetnames']]
    # check that all samples are present
    expected = set(dfix['samples'])
    actual = set(join([df['NAME'] for df in sheets]))
    diff = (actual - expected).union(expected - actual)
    assert len(diff) == 0, \
        f"{diff} samples were not read properly."
    # check that all content names are expected
    expected = set(dfix['print columns'])
    actual = set(sheets[0].columns)
    diff = (actual - expected).union(expected - actual)
    assert len(diff) == 0, \
        f"{diff} columns names were not read properly from 'print' sheet."
    # ibid
    expected = set(dfix['xct columns'])
    actual = set(sheets[1].columns)
    diff = (actual - expected).union(expected - actual)
    assert len(diff) == 0, \
        f"{diff} columns names were not read properly from 'CT' sheet."
    # ibid
    expected = set(dfix['vickers columns'])
    actual = set(sheets[2].columns)
    diff = (actual - expected).union(expected - actual)
    assert len(diff) == 0, \
    f"{diff} columns names were not read properly from 'Vickers' sheet."
    # check contents
    sheet = sheets[2]
    cell = dfix['cells'][0]
    mask = (sheet['NAME'] == cell['name']).values
    actual = sheet[cell['column']].iloc[mask][0]
    expected = cell['value']
    assert all([all([i == j for i,j in zip(a, b)])
                for a, b in zip(actual, expected)]), \
        f'\nguess ({type(actual)}):{actual}\n' \
        f'check ({type(expected)}):{expected}\n'
