#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 23:27:59 2020

@author: crzy
"""

from flask import Blueprint
from pytezos import Contract
from pytezos import pytezos
from pytezos.operation.result import OperationResult

pytezos = pytezos
OperationResult = OperationResult

crowd_api = Blueprint('crowd_api', __name__)

@crowd_api.route('/publish_crowd', methods = ['GET'])
def publish_crowd():
    
    contract = Contract.from_file('./smart_contracts/crowd.tz')    
    op = pytezos.origination(script=contract.script()).autofill().sign().inject(_async=False, num_blocks_wait=2)    
    originated_kt = OperationResult.originated_contracts(op)
    return { 'kt' : originated_kt[0] }

@crowd_api.route
def send_fund():
    pass

@crowd_api.route
def pay_off():
    pass

@crowd_api.route
def refund():
    pass