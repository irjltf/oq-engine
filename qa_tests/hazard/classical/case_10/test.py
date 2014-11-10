# Copyright (c) 2010-2014, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

import StringIO
import numpy
import os
import shutil
import tempfile

from nose.plugins.attrib import attr
from openquake.engine.db import models
from openquake.engine.export import hazard as hazard_export
from openquake.commonlib.tests import check_expected
from qa_tests import _utils as qa_utils


class ClassicalHazardCase10TestCase(qa_utils.BaseQATestCase):

    @attr('qa', 'hazard', 'classical')
    def test(self):
        result_dir = tempfile.mkdtemp()

        try:
            cfg = os.path.join(os.path.dirname(__file__), 'job.ini')
            expected_curve_poes_b1_b2 = [0.00995, 0.00076, 9.7E-5, 0.0]
            expected_curve_poes_b1_b3 = [0.043, 0.0012, 7.394E-5, 0.0]

            job = self.run_hazard(cfg)

            # Test the poe values for the two curves:
            curve_b1_b2, curve_b1_b3 = models.HazardCurveData.objects\
                .filter(hazard_curve__output__oq_job=job.id)\
                .order_by('hazard_curve__lt_realization__lt_model__sm_lt_path')

            # Sanity check, to make sure we have the curves ordered correctly:
            self.assertEqual(
                ['b1', 'b2'],
                curve_b1_b2.hazard_curve.lt_realization.sm_lt_path)
            self.assertEqual(
                ['b1', 'b3'],
                curve_b1_b3.hazard_curve.lt_realization.sm_lt_path)

            numpy.testing.assert_array_almost_equal(
                expected_curve_poes_b1_b2, curve_b1_b2.poes, decimal=4)
            numpy.testing.assert_array_almost_equal(
                expected_curve_poes_b1_b3, curve_b1_b3.poes, decimal=4)

            # Test the exports as well:
            exported_file_b1_b2 = hazard_export.export(
                curve_b1_b2.hazard_curve.output.id, result_dir)
            check_expected(__file__, 'expected_b1_b2.xml',
                           exported_file_b1_b2)

            exported_file_b1_b3 = hazard_export.export(
                curve_b1_b3.hazard_curve.output.id, result_dir)
            check_expected(__file__, 'expected_b1_b3.xml',
                           exported_file_b1_b3)
        except:
            raise
        else:
            shutil.rmtree(result_dir)
