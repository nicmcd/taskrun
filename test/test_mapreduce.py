"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""
import numpy
import random
import unittest
import taskrun
from .ComparisonCheckObserver import ComparisonCheckObserver


rnd = random.Random()
rnd.seed()

def rsleep(m=0.05):
  return 'sleep {0}'.format(rnd.random() * m)

class MapReduceTestCase(unittest.TestCase):
  def test_mapreduce(self):
    vcs = numpy.arange(1, 8+1, 1)
    rates = numpy.arange(5, 100+1, 5)

    ob = ComparisonCheckObserver(0, [], verbose=False)
    tm = taskrun.TaskManager(observers=[ob])

    # build all tasks
    map_all = taskrun.ProcessTask(tm, 'M', rsleep())
    reduce_all = taskrun.ProcessTask(tm, 'R', rsleep())

    for vc in vcs:
      map_vc = taskrun.ProcessTask(tm, 'M_{0}'.format(vc), rsleep())
      map_vc.add_dependency(map_all)

      reduce_vc = taskrun.ProcessTask(tm, 'R_{0}'.format(vc), rsleep())
      reduce_all.add_dependency(reduce_vc)

      for rate in rates:
        worker = taskrun.ProcessTask(tm, 'W_{0}_{1}'.format(vc, rate), rsleep())
        worker.add_dependency(map_vc)
        reduce_vc.add_dependency(worker)

    # build comparison list
    comps = []
    count = 0
    m_s_lt = '+M < -M +R -R '
    m_e_lt = '-M < +R -R '
    r_s_gt = '+R > +M -M '
    r_e_gt = '-R > +R +M -M '

    for vc in vcs:
      m_s_lt += '+M_{0} -M_{0} '.format(vc)
      m_e_lt += '+M_{0} -M_{0} '.format(vc)
      r_s_gt += '+M_{0} -M_{0} '.format(vc)
      r_e_gt += '+M_{0} -M_{0} '.format(vc)

      mv_s_lt = '+M_{0} < -M_{0} +R -R '.format(vc)
      mv_e_lt = '-M_{0} < +R -R '.format(vc)
      rv_e_gt = '+R_{0} > +M -M '.format(vc)
      rv_s_gt = '-R_{0} > +R_{0} +M -M '.format(vc)

      for rate in rates:
        m_s_lt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        m_e_lt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        r_e_gt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        r_s_gt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)

        mv_s_lt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        mv_e_lt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        rv_e_gt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)
        rv_s_gt += '+W_{0}_{1} -W_{0}_{1} '.format(vc, rate)

        w_e_lt = '+W_{0}_{1} < -W_{0}_{1} +R -R '.format(vc, rate)
        w_s_lt = '-W_{0}_{1} < +R -R '.format(vc, rate)
        comps.append(w_s_lt)
        comps.append(w_e_lt)
        count += 2
      comps.append(mv_s_lt)
      comps.append(mv_e_lt)
      comps.append(rv_s_gt)
      comps.append(rv_e_gt)
      count += 4
    comps.append(m_s_lt)
    comps.append(m_e_lt)
    comps.append(r_s_gt)
    comps.append(r_e_gt)
    count += 4

    # re-init the observer
    ob.reinit(count, comps)

    # run and check
    tm.run_tasks()
    self.assertTrue(ob.ok())
