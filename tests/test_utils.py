#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np
import pint

from fairmat_readers_xrd.utils import (
    to_pint_quantity,
    modify_scan_data,
    detect_scan_type,
)

ureg = pint.get_application_registry()


def test_to_pint_quantity():
    assert to_pint_quantity(None, None) is None
    assert to_pint_quantity(None, 'mA') is None
    assert to_pint_quantity('Copper', '') == 'Copper'
    assert to_pint_quantity('Copper', 'mA') == 'Copper'
    assert to_pint_quantity(3.0, '') == 3 * ureg.dimensionless
    assert to_pint_quantity(3.0 * ureg.m, None) == 3 * ureg.m
    assert to_pint_quantity(3.0 * ureg.m, 'cm') == 300 * ureg.cm
    assert to_pint_quantity(1, None) == 1
    assert (
        to_pint_quantity(np.asarray([1.0, 2.0]), 'm') == np.asarray([1.0, 2.0]) * ureg.m
    ).all()
    assert (
        to_pint_quantity(np.asarray([1.0, 2.0]), '')
        == np.asarray([1.0, 2.0]) * ureg.dimensionless
    ).all()
    assert to_pint_quantity(1, 'mA') == 1 * ureg.mA


def test_modify_scan_data():
    data_1D = {
        '2Theta': [np.array([1, 2, 3]) * ureg.deg],
        'Omega': [np.array([2, 2, 2]) * ureg.deg],
        'Chi': [np.array([2]) * ureg.deg],
        'intensity': [np.array([1, 2, 3]) * ureg.dimensionless],
    }
    output = modify_scan_data(data_1D, scan_type='line')
    print(output)
    assert (output['2Theta'] == [1, 2, 3] * ureg.deg).all()
    assert output['Omega'][0] == 2 * ureg.deg
    assert len(output['Omega']) == 1
    assert (output['Chi'] == [2] * ureg.deg).all()
    assert (output['intensity'] == [1, 2, 3] * ureg.dimensionless).all()

    data_RSM = {
        '2Theta': [
            np.array([1, 2, 3]) * ureg.deg,
            np.array([1, 2, 3]) * ureg.deg,
            np.array([1, 2, 3]) * ureg.deg,
        ],
        'Omega': [
            np.array([1]) * ureg.deg,
            np.array([2]) * ureg.deg,
            np.array([3]) * ureg.deg,
        ],
        'Chi': [
            np.array([1]) * ureg.deg,
            np.array([1]) * ureg.deg,
            np.array([1]) * ureg.deg,
        ],
        'intensity': [
            np.array([1, 7, 3]) * ureg.dimensionless,
            np.array([6, 2, 3]) * ureg.dimensionless,
            np.array([4, 1, 3]) * ureg.dimensionless,
        ],
    }
    output = modify_scan_data(data_RSM, scan_type='rsm')
    print(output)
    assert (output['2Theta'] == [[1, 2, 3], [1, 2, 3], [1, 2, 3]] * ureg.deg).all()
    assert (output['Omega'] == [1, 2, 3] * ureg.deg).all()
    assert len(output['Chi']) == 1
    assert (
        output['intensity'] == [[1, 7, 3], [6, 2, 3], [4, 1, 3]] * ureg.dimensionless
    ).all()


def test_detect_scan_type():
    data_1d = {
        '2Theta': [np.array([1, 2, 3]) * ureg.deg],
        'Omega': [np.array([2, 2, 2]) * ureg.deg],
        'Chi': [np.array([2]) * ureg.deg],
        'intensity': [np.array([1, 2, 3]) * ureg.dimensionless],
    }
    data_rsm = {
        '2Theta': [
            np.array([1, 2, 3]) * ureg.deg,
            np.array([1, 2, 3]) * ureg.deg,
            np.array([1, 2, 3]) * ureg.deg,
        ],
        'Omega': [
            np.array([1]) * ureg.deg,
            np.array([2]) * ureg.deg,
            np.array([3]) * ureg.deg,
        ],
        'Chi': [
            np.array([1]) * ureg.deg,
            np.array([1]) * ureg.deg,
            np.array([1]) * ureg.deg,
        ],
        'intensity': [
            np.array([1, 7, 3]) * ureg.dimensionless,
            np.array([6, 2, 3]) * ureg.dimensionless,
            np.array([4, 1, 3]) * ureg.dimensionless,
        ],
    }

    data_multiline1 = data_rsm.copy()
    data_multiline1['2Theta'] = (
        [
            np.array([1, 2, 3]) * ureg.deg,
            np.array([1, 2, 3, 4]) * ureg.deg,
            np.array([1, 3, 3]) * ureg.deg,
        ],
    )
    data_multiline1['intensity'] = [
        np.array([1, 7, 3]) * ureg.dimensionless,
        np.array([6, 2, 3, 4]) * ureg.dimensionless,
        np.array([4, 1, 3]) * ureg.dimensionless,
    ]

    data_multiline2 = data_rsm.copy()
    data_multiline2['2Theta'] = [
        np.array([1, 2, 3]) * ureg.deg,
        np.array([4, 5, 6]) * ureg.deg,
        np.array([1, 2, 3]) * ureg.deg,
    ]

    data_multiline3 = data_rsm.copy()
    data_multiline3['Chi'] = [
        np.array([1]) * ureg.deg,
        np.array([2]) * ureg.deg,
        np.array([3]) * ureg.deg,
    ]

    for data in [data_1d]:
        scan_type = detect_scan_type(data)
        assert scan_type == 'line'
    for data in [data_rsm]:
        scan_type = detect_scan_type(data)
        assert scan_type == 'rsm'
    for data in [
        data_multiline1,
        data_multiline2,
        data_multiline3,
    ]:
        scan_type = detect_scan_type(data)
        assert scan_type == 'multiline'
