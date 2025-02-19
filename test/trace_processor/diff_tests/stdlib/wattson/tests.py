#!/usr/bin/env python3
# Copyright (C) 2024 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from python.generators.diff_tests.testing import Csv, Path, DataPath
from python.generators.diff_tests.testing import DiffTestBlueprint
from python.generators.diff_tests.testing import TestSuite


class WattsonStdlib(TestSuite):
  consolidate_tables_template = ('''
      SELECT
        sum(dur) as duration,
        SUM(l3_hit_count) AS l3_hit_count,
        SUM(l3_miss_count) AS l3_miss_count,
        freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
        freq_4, idle_4, freq_5, idle_5, freq_6, idle_6, freq_7, idle_7,
        suspended
      FROM SYSTEM_STATE_TABLE
      GROUP BY
        freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
        freq_4, idle_4, freq_5, idle_5, freq_6, idle_6, freq_7, idle_7,
        suspended
      ORDER BY duration desc
      LIMIT 20;
      ''')

  # Test raw system state before any grouping
  def test_wattson_system_state(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;
        SELECT * from wattson_system_states
        ORDER by ts DESC
        LIMIT 20
        """,
        out=Csv("""
        "ts","dur","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
        370103436540,339437,"[NULL]","[NULL]",738000,-1,738000,1,738000,-1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103419857,16683,"[NULL]","[NULL]",738000,-1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103413314,6543,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103079729,333585,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,-1,1106000,1,0
        370103037378,42351,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,1,400000,1,1106000,-1,1106000,1,0
        370102869076,168302,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,1,400000,1,1106000,-1,1106000,-1,0
        370102832862,36214,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,1106000,-1,1106000,-1,0
        370102831844,1018,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,1106000,-1,984000,-1,0
        370102819475,12369,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102816586,1098,"[NULL]","[NULL]",738000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102669043,147543,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102244564,424479,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,1,400000,1,400000,1,984000,-1,984000,-1,0
        370100810360,1434204,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,1,400000,1,400000,1,984000,1,984000,-1,0
        370100731096,79264,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100411312,319784,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100224219,187093,"[NULL]","[NULL]",574000,-1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100171729,52490,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370096612858,3558871,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,1,984000,-1,0
        370096452775,160083,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,-1,984000,-1,0
        370096347307,105468,"[NULL]","[NULL]",574000,-1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,-1,984000,-1,0
            """))

  # Test fixup of deep idle offset and time marker window.
  def test_wattson_time_window(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;

        CREATE PERFETTO TABLE wattson_time_window
        AS
        SELECT 362426061658 AS ts, 5067704349 AS dur;

        -- Final table that is cut off to fit within the requested time window.
        CREATE VIRTUAL TABLE time_window_intersect
          USING SPAN_JOIN(wattson_system_states, wattson_time_window);
        """ + self.consolidate_tables_template.replace("SYSTEM_STATE_TABLE",
                                                       "time_window_intersect"),
        out=Csv("""
            "duration","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
            58982760,2787779,1229222,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,1,500000,0,0
            50664181,2364802,1133322,574000,0,574000,1,574000,1,574000,0,553000,1,553000,0,500000,0,500000,0,0
            41743544,2013295,917107,574000,0,574000,0,574000,1,574000,1,553000,0,553000,0,500000,0,500000,1,0
            33801135,1479851,684489,300000,0,300000,0,300000,1,300000,1,400000,0,400000,0,500000,0,500000,1,0
            32703489,1428203,690001,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            29062133,1597555,719900,574000,0,574000,0,574000,1,574000,0,553000,1,553000,0,500000,1,500000,0,0
            28310872,1211262,566873,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            26754474,1224826,569901,300000,0,300000,1,300000,0,300000,0,400000,1,400000,0,500000,0,500000,0,0
            25107621,1059311,473161,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,1,500000,0,0
            23771603,987803,450930,300000,0,300000,1,300000,1,300000,0,400000,1,400000,0,500000,0,500000,0,0
            23721891,963220,409196,300000,0,300000,0,300000,1,300000,0,400000,1,400000,0,500000,1,500000,0,0
            22988523,984240,473025,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,1,0
            21790436,987511,449348,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,0,500000,1,0
            21673975,1034856,445803,574000,0,574000,0,574000,1,574000,0,553000,0,553000,0,500000,0,500000,1,0
            20665650,974100,442861,300000,0,300000,0,300000,1,300000,0,400000,0,400000,1,500000,0,500000,0,0
            18024891,823424,339250,300000,0,300000,1,300000,0,300000,0,400000,0,400000,0,500000,1,500000,0,0
            17669272,826030,346995,574000,0,574000,0,574000,0,574000,0,553000,1,553000,0,500000,1,500000,0,0
            16774291,762738,348469,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,0,500000,1,0
            16191449,689792,316923,300000,0,300000,0,300000,1,300000,0,400000,1,400000,0,500000,0,500000,0,0
            15918895,742531,325426,574000,0,574000,1,574000,0,574000,1,553000,0,553000,0,500000,1,500000,0,0
            """))

  # Test on Raven for checking system states and the DSU PMU counts.
  def test_wattson_dsu_pmu(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("INCLUDE PERFETTO MODULE wattson.system_state;\n" +
               self.consolidate_tables_template.replace(
                   "SYSTEM_STATE_TABLE", "wattson_system_states")),
        out=Csv("""
            "duration","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
            1279130692,1318302,419159,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            165854009,118369,42037,300000,-1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            121156343,5846554,2343180,574000,0,574000,1,574000,0,574000,0,553000,0,553000,0,500000,1,500000,1,0
            72876331,133532,57759,300000,1,300000,1,300000,-1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            71060865,69029,22056,300000,1,300000,-1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            64501262,276098,309757,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,-1,500000,1,0
            58982760,2787779,1229222,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,1,500000,0,0
            51127388,50724,18075,300000,1,300000,1,300000,1,300000,-1,400000,1,400000,1,500000,1,500000,1,0
            50664181,2364802,1133322,574000,0,574000,1,574000,1,574000,0,553000,1,553000,0,500000,0,500000,0,0
            49948122,2216740,934893,300000,0,300000,1,300000,0,300000,0,400000,0,400000,0,500000,1,500000,1,0
            41743544,2013295,917107,574000,0,574000,0,574000,1,574000,1,553000,0,553000,0,500000,0,500000,1,0
            40606558,"[NULL]","[NULL]",1401000,1,1401000,1,1401000,1,1401000,1,400000,1,400000,1,2802000,1,2802000,1,0
            39887541,14272,1252,300000,0,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            38159789,1428203,690001,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            33801135,1479851,684489,300000,0,300000,0,300000,1,300000,1,400000,0,400000,0,500000,0,500000,1,0
            31543574,34702,18036,300000,1,300000,1,300000,1,300000,1,400000,-1,400000,1,500000,1,500000,1,0
            31470669,163778,200331,1098000,1,1098000,1,1098000,1,1098000,1,400000,1,400000,1,500000,1,500000,-1,0
            30993650,39579,48376,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,-1,0
            30144287,1396131,585581,574000,0,574000,1,574000,0,574000,0,553000,0,553000,0,500000,1,500000,0,0
            30009881,"[NULL]","[NULL]",1328000,1,1328000,1,1328000,1,1328000,1,2253000,1,2253000,1,500000,1,500000,1,0
            """))

  # Test on eos to check that suspend states are being calculated appropriately.
  def test_wattson_suspend(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;
        SELECT
          sum(dur) as duration,
          freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
          suspended
        FROM wattson_system_states
        GROUP BY
          freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
          suspended
        ORDER BY duration desc
        LIMIT 20;
        """,
        out=Csv("""
            "duration","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","suspended"
            16606175990,614400,1,614400,1,614400,1,614400,1,0
            10648392546,1708800,-1,1708800,-1,1708800,-1,1708800,-1,1
            6933558399,1708800,-1,1708800,-1,1708800,-1,1708800,-1,0
            1649400745,614400,0,614400,0,614400,0,614400,0,0
            1199187488,614400,-1,614400,1,614400,1,614400,1,0
            945900007,1708800,0,1708800,0,1708800,0,1708800,0,0
            936351409,1363200,0,1363200,0,1363200,0,1363200,1,0
            708490325,1708800,0,1708800,0,1708800,0,1708800,1,0
            706695995,1708800,1,1708800,1,1708800,1,1708800,1,0
            656873956,1363200,1,1363200,1,1363200,1,1363200,1,0
            633440914,1363200,0,1363200,0,1363200,0,1363200,0,0
            627708654,1708800,-1,1708800,0,1708800,0,1708800,0,0
            620315547,1708800,-1,1708800,1,1708800,1,1708800,1,0
            578173274,1708800,-1,1708800,0,1708800,0,1708800,-1,0
            530967964,1708800,-1,1708800,-1,1708800,0,1708800,-1,0
            516281990,1708800,0,1708800,0,1708800,0,1708800,-1,0
            473910837,1363200,-1,1363200,0,1363200,0,1363200,1,0
            461831724,1708800,0,1708800,-1,1708800,0,1708800,0,0
            402233299,1708800,-1,1708800,-1,1708800,-1,1708800,1,0
            375051979,864000,1,864000,1,864000,1,864000,1,0
            """))

  # Test that the device name can be extracted from the trace's metadata.
  def test_wattson_device_name(self):
    return DiffTestBlueprint(
        trace=DataPath('android_cpu_eos.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.device_infos;
            select name from _wattson_device
            """),
        out=Csv("""
            "name"
            "monaco"
            """))
