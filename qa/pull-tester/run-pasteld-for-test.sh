#!/bin/bash
# Copyright (c) 2013-2014 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#
PASTEL_LOAD_TIMEOUT=500
DATADIR="/home/akobrin/p/Pastel/.pastel"
rm -rf "$DATADIR"
mkdir -p "$DATADIR"/regtest
touch "$DATADIR/pastel.conf"
touch "$DATADIR/regtest/debug.log"
tail -q -n 1 -F "$DATADIR/regtest/debug.log" | grep -m 1 -q "Done loading" &
WAITER=$!
PORT=`expr 10000 + $$ % 55536`
"/home/akobrin/p/Pastel/src/pasteld" -connect=0.0.0.0 -datadir="$DATADIR" -rpcuser=user -rpcpassword=pass -listen -keypool=3 -debug -debug=net -logtimestamps -checkmempool=0 -relaypriority=0 -port=$PORT -whitelist=127.0.0.1 -regtest -rpcport=`expr $PORT + 1` &
PASTELD=$!

#Install a watchdog.
(sleep "$PASTEL_LOAD_TIMEOUT" && kill -0 $WAITER 2>/dev/null && kill -9 $PASTELD $$)&
wait $WAITER

if [ -n "$TIMEOUT" ]; then
  timeout "$TIMEOUT"s "$@" $PORT
  RETURN=$?
else
  "$@" $PORT
  RETURN=$?
fi

(sleep "$PASTEL_LOAD_TIMEOUT" && kill -0 $PASTELD 2>/dev/null && kill -9 $PASTELD $$)&
kill $PASTELD && wait $PASTELD

# timeout returns 124 on timeout, otherwise the return value of the child

# If $RETURN is not 0, the test failed. Dump the tail of the debug log.
if [ $RETURN -ne 0 ]; then tail -n 200 $DATADIR/regtest/debug.log; fi

exit $RETURN
