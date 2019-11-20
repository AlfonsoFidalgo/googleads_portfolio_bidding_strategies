from googleads import adwords
import pandas as pd

def get_client():
    return adwords.AdWordsClient.LoadFromStorage('./googleads.yaml')

def get_bidding_strategies(client):
    '''
    Returns your client's portfolio bidding strategies
    '''
    bidding_strategies = client.GetService('BiddingStrategyService', version='v201809')
    selector = {'fields': ['BiddingScheme', 'Id', 'Name', 'Status', 'Type'],
                'predicates': [{'field':'Status', 'operator': 'EQUALS', 'values': 'ENABLED'}]}
    return bidding_strategies.get(selector)

def remove_strategy_max_bid(portfolio_strategy):
    '''
    Removes any bid limitation that yout portfolio bidding strategy might have
    '''
    bidding_strategies = client.GetService('BiddingStrategyService', version='v201809')
    operations = [{'operator': 'SET',
                   'operand': portfolio_strategy}]
    res = bidding_strategies.mutate(operations)


def set_tcpa_bid_limit(portfolio_strategy, limit):
    '''
    Sets a bid limitation for your tCPA bidding strategy
    portfolio_strategy: AdWords API portfolio object
    limit: the actual limit
    '''
    bidding_strategies = client.GetService('BiddingStrategyService', version='v201809')
    limit = int(limit * 1000000)
    portfolio_strategy['biddingScheme']['maxCpcBidCeiling'] = {'ComparableValue.Type': 'Money', 'microAmount': limit} 
    operations = [{'operator': 'SET',
                   'operand': portfolio_strategy}]
    res = bidding_strategies.mutate(operations)


def adjust_limit(portfolio_strategy, action, adjust):
    '''
    Increases or decreases the bid limitation by the adjust %
    portfolio_strategy: AdWords API portfolio object
    action: 'increase' or 'decrease'
    adjust: percent
    '''
    bidding_strategies = client.GetService('BiddingStrategyService', version='v201809')
    bid_limit = portfolio_strategy['biddingScheme']['maxCpcBidCeiling']['microAmount']
    adjust_amount = bid_limit * adjust
    if action == 'decrease':
        new_limit = bid_limit - adjust_amount
    elif action == 'increase':
        new_limit = bid_limit + adjust_amount
    else:
        return
    portfolio_strategy['biddingScheme']['maxCpcBidCeiling']['microAmount'] = int(new_limit) 
    operations = [{'operator': 'SET',
                   'operand': portfolio_strategy}]
    res = bidding_strategies.mutate(operations)


def decrease_tcpa(portfolios, decrease=0.1, min_target=18):
    '''
    Reduces tCPA targets across a given account
    portfolios: your account's tCPA portfolio tCPA strategies
    decrease: percentage by which the target will decrease
    min_target: minimum tCPA target
    '''
    bidding_strategies = client.GetService('BiddingStrategyService', version='v201809')
    for portfolio in portfolios:
        if portfolio['biddingScheme'] is not None:
            if portfolio['type'] == 'TARGET_CPA':
                target = portfolio['biddingScheme']['targetCpa']['microAmount'] / 1000000
                if target > 18:
                    new_target = target - (target * decrease)
                    new_target_filtered = max(min_target, new_target)
                    portfolio['biddingScheme']['targetCpa'] = {'ComparableValue.Type': 'Money', 'microAmount': int(new_target_filtered * 1000000)}
                    operations = [{'operator': 'SET',
                                   'operand': portfolio}]
                    res = bidding_strategies.mutate(operations)
                    print(portfolio['name'], ' target changed from ', target, ' to ', new_target_filtered)


