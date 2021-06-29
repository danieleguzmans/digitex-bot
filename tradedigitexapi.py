import config
import asyncio
import random
from decimal import Decimal

from digitex_bot_framework import *

market = Market.BTC_USD
print(f'market: {market}')
trader = market.trader
print(f'trader: {trader}')


async def place_an_order():
    last_trade = market.last_trade
    print(f'last trade: {last_trade}')
    rounded_spot_price = market.rounded_spot_price()
    print(f'rounded spot price {rounded_spot_price}')
    if rounded_spot_price is None or last_trade is None:
        print('Skipped placing an order due to unknown price')
        return

    quantity = 5000

    if rounded_spot_price < last_trade.price:
        print('SELL')
        side = OrderSide.SELL
        print(f'side SELL: {side}')
    elif rounded_spot_price > last_trade.price:
        print('BUY')
        side = OrderSide.BUY
        print(f'side BUY: {side}')
    else:
        if trader.position.type == PositionType.LONG:
            print(
                'SELL - trader.position.type: {trader.position.type} = PositionType: {PositionType.LONG}')
            side = OrderSide.SELL
            print(f'side SELL: {side}')
        elif trader.position.type == PositionType.SHORT:
            print(
                f'BUY - trader.position.type: {trader.position.type} == PositionType.SHORT: {PositionType.SHORT}')
            side = OrderSide.BUY
        else:
            side = random.choice([OrderSide.BUY, OrderSide.SELL])
            print('Random SELL or BUY - side: {side}')

    print(f'Placing an order for {quantity} at {rounded_spot_price}')
    order = Order(price=rounded_spot_price, quantity=quantity, side=side)
    await trader.orders.place(order)


async def on_currency_pair_update():
    if market.last_trade is not None and market.rounded_spot_price() != market.last_trade.price:
        # Better act fast!
        await place_an_order()

market.currency_pair.on_update = on_currency_pair_update
print(f'market.currency_pair.on_update: {market.currency_pair.on_update}')


async def main():
    bot = Bot(
        host=config.HOST_DIGITEX_TEST,
        token=config.TOKEN_DIGITEX_TEST
    )

    await bot.add_market(market)

    while True:
        await asyncio.sleep(60000)
        await place_an_order()

asyncio.run(main())
