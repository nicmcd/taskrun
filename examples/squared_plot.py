#!/usr/bin/env python3

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

import argparse
import termplotlib
import numpy
import os
import taskrun
import time
import sys

def square(outputs, index, value, sleep):
  time.sleep(sleep)
  outputs[index] = value * value

def main(args):
  kSize = 100
  outputs = numpy.zeros(kSize, dtype=numpy.float64)

  rm = taskrun.ResourceManager(
    taskrun.CounterResource('cpus', 1, os.cpu_count()))
  ob = taskrun.VerboseObserver(
    timer=args.timer,
    log=args.log,
    show_starts=args.show_starts,
    show_completes=args.show_completes,
    show_bypasses=args.show_bypasses,
    show_failures=args.show_failures,
    show_kills=args.show_kills,
    show_progress=args.show_progress,
    show_summary=args.show_summary,
    show_descriptions=args.show_descriptions,
    show_current_time=args.show_current_time,
  )
  tm = taskrun.TaskManager(resource_manager=rm, observers=[ob])

  values = numpy.linspace(1, 10, kSize)
  for tid, value in enumerate(values):
    taskrun.FunctionTask(tm, 'task_{}'.format(tid), square, outputs, tid, value,
                         args.sleep)

  tm.run_tasks()

  fig = termplotlib.figure()
  fig.plot(values, outputs, width=80, height=40, title='x^2')
  fig.show()

if __name__ == '__main__':
  ap = argparse.ArgumentParser()

  ap.add_argument('--sleep', type=float, default=0.0,
                  help='Time to sleep in each task')

  if taskrun.VerboseObserver.TIMER_DEFAULT:
    ap.add_argument('--timer', action='store_false', help='Disable timer')
  else:
    ap.add_argument('--timer', action='store_true', help='Enable timer')

  ap.add_argument('--log', type=str,
                  default=taskrun.VerboseObserver.LOG_DEFAULT,
                  help='Log file output')

  if taskrun.VerboseObserver.SHOW_STARTS_DEFAULT:
    ap.add_argument('--show_starts', action='store_false',
                    help='Don\'t show task starts')
  else:
    ap.add_argument('--show_starts', action='store_true',
                    help='Show task starts')

  if taskrun.VerboseObserver.SHOW_COMPLETES_DEFAULT:
    ap.add_argument('--show_completes', action='store_false',
                    help='Don\'t show task completes')
  else:
    ap.add_argument('--show_completes', action='store_true',
                    help='Show task completes')

  if taskrun.VerboseObserver.SHOW_BYPASSES_DEFAULT:
    ap.add_argument('--show_bypasses', action='store_false',
                    help='Don\'t show task bypasses')
  else:
    ap.add_argument('--show_bypasses', action='store_true',
                    help='Show task bypasses')

  if taskrun.VerboseObserver.SHOW_FAILURES_DEFAULT:
    ap.add_argument('--show_failures', action='store_false',
                    help='Don\'t show task failures')
  else:
    ap.add_argument('--show_failures', action='store_true',
                    help='Show task failures')

  if taskrun.VerboseObserver.SHOW_KILLS_DEFAULT:
    ap.add_argument('--show_kills', action='store_false',
                    help='Don\'t show task kills')
  else:
    ap.add_argument('--show_kills', action='store_true',
                    help='Show task kills')

  if taskrun.VerboseObserver.SHOW_PROGRESS_DEFAULT:
    ap.add_argument('--show_progress', action='store_false',
                    help='Don\'t show progress')
  else:
    ap.add_argument('--show_progress', action='store_true',
                    help='Show progress')

  if taskrun.VerboseObserver.SHOW_SUMMARY_DEFAULT:
    ap.add_argument('--show_summary', action='store_false',
                    help='Don\'t show summary')
  else:
    ap.add_argument('--show_summary', action='store_true',
                    help='Show summary')

  if taskrun.VerboseObserver.SHOW_DESCRIPTIONS_DEFAULT:
    ap.add_argument('--show_descriptions', action='store_false',
                    help='Don\'t show task descriptions')
  else:
    ap.add_argument('--show_descriptions', action='store_true',
                    help='Show task descriptions')

  if taskrun.VerboseObserver.SHOW_CURRENT_TIME_DEFAULT:
    ap.add_argument('--show_current_time', action='store_false',
                    help='Don\'t show current_time')
  else:
    ap.add_argument('--show_current_time', action='store_true',
                    help='Show current_time')

  args = ap.parse_args()
  sys.exit(main(args))
