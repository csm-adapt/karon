import pytest
from karon import Sample
from karon.decorators import readwrite, requires
from karon.io.excel import ExcelIO
from karon.io.pandas import to_dataframe


@pytest.fixture
def qm_data():
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


@pytest.fixture
def example_data():
    return {
        'filename': 'data/example.xlsx',
        'sheetnames': [
            'build',
            'mechanical',
            'porosity'
        ],
        'samples': [
            'e4f6efde-abdb-4a02-a25a-3c3859857aee',
            'e8a80a70-18cc-44b9-8668-4f479918f13a',
            '398a8f61-9707-45d8-802d-84bd11179a56',
            'e0276301-425d-4d14-9bb4-05c6e3414772',
            '2983b9dd-227a-4136-83c6-473e2deac44d',
            '85bf6cf2-22ac-49e8-862d-f192781f73a3',
            '5b91f720-6a2f-456b-a14f-bb961d1f80dd',
            '94073a4f-cd2f-46dc-95c0-37d60b32e9ad',
            '7bc7c8e8-dcc6-4317-8518-d600f26573ed',
            'e0b7b18c-d025-4beb-856a-7a0f054c9ea2',
            'c1e2c204-62f3-4ed6-9226-35747a43fb9c',
            'b397eac8-87a0-47c4-b5ab-f9514bf50bfa',
            '5022fa10-98d1-4dc0-b35e-4e800ab3cce6',
            'd9e2da61-80dc-9521-2c6b-9e31c4999d81',
            '3036de92-0d52-4f51-a0c0-422f5ad3d8db',
            'd887d4d2-d9ab-4673-8d69-d0daf8af8551',
            '11fe2186-ba63-4b69-8735-25fee5cda5d4',
            '3a50216b-50b3-4212-b7fe-4bd96605556f',
            'c37290e2-1f8e-8820-8ef5-9adc49859d44',
            'e6b3b1c3-ad38-4fc1-82cf-7e301a4aba90',
            'e224bfca-f917-40de-ad6d-12b70e21b456',
            'f29ebef4-7f77-4048-a1e3-2af0ca3f046f'
        ],
        'build columns': [
            'name',
            'parent name',
            'composition',
            'laser power (W)',
            'laser speed (mm/s)',
            'hatch spacing (mm)',
            'spot size (um)'
        ],
        'mechanical columns': [
            'name',
            'parent name',
            'modulus (GPa)',
            'yield strength (MPa)'
        ],
        'porosity columns': [
            'name',
            'parent name',
            'max pore size (um)',
            'neighbor (um)'
        ]
    }


def test_examples(example_data):
    @readwrite
    @requires("name", "parent name")
    def generic(**contents):
        return Sample(**contents)


    expected = example_data
    actual = ExcelIO(build=generic,
                     mechanical=generic,
                     porosity=generic).load(expected['filename'])
    # ##### expected usage ##### #
    names = set(node.contents['name'] for node in actual)
    assert names == set(expected['samples'])
    columns = set()
    for key in ('build columns', 'mechanical columns', 'porosity columns'):
        columns = columns.union(expected[key])
    assert set(to_dataframe(actual).columns) == columns