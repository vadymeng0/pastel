#!/usr/bin/env python3
# Copyright (c) 2016 The Zcash developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php .

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, initialize_chain_clean, \
    start_nodes, connect_nodes_bi, wait_and_assert_operationid_status

import time
from decimal import Decimal, getcontext
getcontext().prec = 16

class WalletTreeStateTest (BitcoinTestFramework):

    def setup_chain(self):
        print(f'Initializing test directory {self.options.tmpdir}')
        initialize_chain_clean(self.options.tmpdir, 4)

    def setup_network(self, split=False):
        self.nodes = start_nodes(3, self.options.tmpdir, extra_args=[['-debug=zrpc']] * 3 )
        connect_nodes_bi(self.nodes,0,1)
        connect_nodes_bi(self.nodes,1,2)
        connect_nodes_bi(self.nodes,0,2)
        self.is_network_split=False
        self.sync_all()

    def run_test (self):
        print("Mining blocks...")

        self.nodes[0].generate(100)
        self.sync_all()
        self.nodes[1].generate(101)
        self.sync_all()

        mytaddr = self.nodes[0].getnewaddress()     # where coins were mined
        myzaddr = self.nodes[0].z_getnewaddress('sprout')

        # Spend coinbase utxos to create three notes of ... each
        recipients = []
        recipients.append({"address":myzaddr, "amount":self._reward - self._fee})
        myopid = self.nodes[0].z_sendmany(mytaddr, recipients)
        wait_and_assert_operationid_status(self.nodes[0], myopid)
        self.sync_all()
        self.nodes[1].generate(1)
        self.sync_all()
        myopid = self.nodes[0].z_sendmany(mytaddr, recipients)
        wait_and_assert_operationid_status(self.nodes[0], myopid)
        self.sync_all()
        self.nodes[1].generate(1)
        self.sync_all()
        myopid = self.nodes[0].z_sendmany(mytaddr, recipients)
        wait_and_assert_operationid_status(self.nodes[0], myopid)
        self.sync_all()
        self.nodes[1].generate(1)
        self.sync_all()

        # Check balance
        resp = self.nodes[0].z_getbalance(myzaddr)
        assert_equal(Decimal(resp), (self._reward-self._fee) * 3 )

        # We want to test a real-world situation where during the time spent creating a transaction
        # with joinsplits, other transactions containing joinsplits have been mined into new blocks,
        # which result in the treestate changing whilst creating the transaction.

        # Tx 1 will change the treestate while Tx 2 containing chained joinsplits is still being generated
        recipients = []
        recipients.append({"address":self.nodes[2].z_getnewaddress("sprout"), "amount":self._reward - self._fee})
        myopid = self.nodes[0].z_sendmany(mytaddr, recipients)
        wait_and_assert_operationid_status(self.nodes[0], myopid)

        # Tx 2 will consume all three notes, which must take at least two joinsplits.  This is regardless of
        # the z_sendmany implementation because there are only two inputs per joinsplit.
        recipients = []
        recipients.append({"address":self.nodes[2].z_getnewaddress("sprout"), "amount":Decimal('18')})
        recipients.append({"address":self.nodes[2].z_getnewaddress("sprout"), "amount":(self._reward-self._fee)*3 - Decimal('18') - self._fee})
        myopid = self.nodes[0].z_sendmany(myzaddr, recipients)

        # Wait for Tx 2 to begin executing...
        for x in range(1, 60):
            results = self.nodes[0].z_getoperationstatus([myopid])
            status = results[0]["status"]
            if status == "executing":
                break
            time.sleep(1)

        # Now mine Tx 1 which will change global treestate before Tx 2's second joinsplit begins processing
        self.sync_all()
        self.nodes[1].generate(1)
        self.sync_all()

        # Wait for Tx 2 to be created
        wait_and_assert_operationid_status(self.nodes[0], myopid)

        # Note that a bug existed in v1.0.0-1.0.3 where Tx 2 creation would fail with an error:
        # "Witness for spendable note does not have same anchor as change input"

        # Check balance
        resp = self.nodes[0].z_getbalance(myzaddr)
        assert_equal(Decimal(resp), Decimal('0.0'))


if __name__ == '__main__':
    WalletTreeStateTest().main()
