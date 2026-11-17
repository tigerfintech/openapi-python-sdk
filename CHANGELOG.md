# Changelog

## 3.9.2 (2026-11-18)

### New

- Contract responses expose supported combinations of order types, time in force, and trading sessions through order capabilities.

## 3.9.1 (2026-11-09)

### New

- US option snapshots and option chains provide GTH/CURB extended-session quotes and independent cumulative volume and turnover.
- Protobuf option callbacks provide current-session prices, volume, and turnover with `PreMarket` / `AfterHours` tags and independent cumulative totals.
- Option minute-bar requests support `with_hour_trading` to include or exclude extended-session data while preserving the server default when omitted.

### Changed

- Protobuf option callbacks use flat quote fields; HTTP snapshots and option chains retain their extended-session objects.

## 3.9.0 (2026-11-04)

### New

- The `tigeropen.news` module provides `NewsClient`.
- `get_stock_news` queries one stock's news with page-number pagination.
- `get_market_news` queries market highlights with cursor pagination.
- News queries support simplified Chinese, traditional Chinese, and English. Omitting the language inherits the client setting; an empty string requests mixed-language content, and unsupported values fall back to English.
- News responses include pagination, titles, summaries, publication timestamps, and article URLs.

## 3.8.1 (2026-09-23)

### New

- Asset and position queries support `asset_quote_type` values `ETH`, `RTH`, and `OVERNIGHT`.
- Asset and position subscriptions accept a quote basis.
- The CLI supports `--asset-quote-type`.

### Changed

- Existing behavior is preserved when no quote basis is specified.
- Subscription quote-basis selection requires Protobuf; STOMP reports an error if the parameter is supplied.

## 3.8.0 (2026-09-17)

### New

- OAuth2 authentication supports automatic token storage and renewal through `OAuth2SessionManager` and `OAuth2Authentication`.
- Push connections renew OAuth2 tokens without reconnecting.
- The CLI provides authentication commands, OAuth2 configuration, and a global account option.

### Changed

- Existing tigerId and private-key authentication remains available when no alternative authentication is configured.

## 3.7.2 (2026-08-27)

### New

- Real-time stock and cryptocurrency quotes provide turnover through `QuoteBrief.amount`.

## 3.7.1 (2026-08-19)

### New

- Option chains provide current and previous mark prices, midpoint prices, and their timestamps.

## 3.7.0 (2026-07-23)

### New

- `get_corporate_symbol_change` queries stock symbol changes.
- `get_corporate_delisting` queries delisting events.
- `get_corporate_ipo` queries IPO events.
- `CorporateActionType` includes `SYMBOL_CHANGE`, `DELISTING`, and `IPO`.

## 3.6.0 (2026-06-24)

### New

- `iceberg_order` creates iceberg orders.
- `PriceType` supports limit, ask, bid, and latest prices.

## 3.5.9 (2026-06-08)

### New

- Option-exercise APIs support early exercise and lapse requests, cancellation, position-change checks, filtered records, and eligible-position queries.
- Order push messages provide order-information and order-status update timestamps.

## 3.5.8 (2026-04-24)

### New

- The CLI stock scanner supports numeric, accumulated, financial, and tag filters, preset gainers/losers filters, sorting, and result limits.
- A PowerShell installer supports Windows; shell installations on Windows provide PowerShell guidance.

### Fixed

- Configuration file paths retain custom filenames.
- The account-assets command renders portfolio accounts correctly.

## 3.5.7 (2026-03-25)

### Fixed

- Installation works with older pip and setuptools versions.
- Incompatible Protobuf versions no longer prevent all CLI commands from starting; push commands report an upgrade requirement.

## 3.5.6 (2026-03-24)

### New

- The `tigeropen` CLI supports configuration, quotes, trading, accounts, and push subscriptions, with table, JSON, and CSV output.
- One-step installation and automatic uninstallation are available.
- AI coding tools can use the supplied SDK skills.
- The package supports modern Python build tools.

### Changed

- Documentation is available at docs.itigerup.com with bilingual CLI, MCP, and skills guidance.

## 3.5.5 (2026-03-12)

### New

- Option analysis supports historical volatility lists through `require_volatility_list`.

## 3.5.4 (2026-03-02)

### New

- Quote, trading, and push APIs support cryptocurrency.
- Monetary orders are supported.

## 3.5.3 (2026-01-29)

### New

- `get_option_analysis` provides implied and historical volatility, IV/HV ratios, call/put ratios, IV percentiles, and IV ranks.

## 3.5.2 (2026-01-21)

### New

- Option quotes provide mark prices, selling returns, and related fields.
- Additional option-calculation helpers are available.

### Changed

- cryptography 41.0.7 or later is required.

## 3.5.1 (2025-12-26)

### New

- Trading clients support position-transfer APIs.

## 3.5.0 (2025-12-22)

### New

- Transaction queries accept date ranges and provide quantity scales.
- Prime-account assets provide foreign-exchange rates.
- Push callbacks support thread pools.

## 3.4.9 (2025-10-28)

### New

- `get_bars` supports `with_fundamental` to include valuation and turnover data.

## 3.4.8 (2025-09-24)

### New

- `get_future_history_main_contract` queries historical main futures contracts.

## 3.4.7 (2025-09-23)

### Fixed

- Historical timelines parse pre-market and post-market data correctly.

### Breaking

- The `get_timeline` DataFrame column `tradingSession` is renamed to `trade_session`, with string values from the `TradingSession` enum.

## 3.4.6 (2025-08-28)

### New

- Position contracts provide instrument and underlying-contract names.

### Changed

- Improved MCP server behavior.

## 3.4.5 (2025-08-22)

### New

- `get_future_depth` queries futures depth.
- Stock depth, ticks, timelines, historical timelines, and bars support overnight queries through `trade_session`.
- An MCP server beta is available.

## 3.4.4 (2025-07-31)

### New

- Stock scanning supports cursor pagination.

## 3.4.3 (2025-07-22)

### Fixed

- Order placement handles the response's orders attribute correctly.

## 3.4.2 (2025-07-18)

### New

- Order helpers accept time in force.
- Futures contracts provide contract value, delivery mode, and product type.
- Futures quotes provide changes in open interest.

### Breaking

- Order and transaction queries support `page_token`. When supplied, the return value is a response object instead of a list; use `.result` for items and `.next_page_token` for the next cursor.

## 3.4.1 (2025-06-26)

### New

- `get_option_timeline` queries option timelines.
- Contracts indicate fractional-share support.

## 3.4.0 (2025-06-17)

### New

- `get_bars` accepts a date for historical minute bars.
- Additional APIs accept a language option.

### Changed

- The default client language is English.

## 3.3.9 (2025-06-12)

### New

- Order callbacks provide time in force.

## 3.3.8 (2025-05-29)

### New

- Configuration supports the TBUS license.
- Order preview is supported.

## 3.3.7 (2025-05-12)

### New

- Order callbacks provide order attributes.
- Subscription methods return subscription IDs.

## 3.3.6 (2025-04-28)

### New

- `get_fund_details` queries funding details.
- Option APIs accept timezone options.

### Changed

- Legacy `sandbox_config` configuration is deprecated.

## 3.3.5 (2025-04-11)

### New

- `get_broker_hold` queries broker holdings by market value.

## 3.3.4 (2025-04-09)

### New

- `get_aggregate_assets` queries aggregate assets.

### Changed

- Stock-scanner fields are updated.

## 3.3.3 (2025-03-05)

### New

- `get_quote_overnight` queries overnight quotes.
- Contracts indicate overnight-trading support.

## 3.3.2 (2025-02-25)

### New

- `get_trade_rank` queries popular trading rankings.
- Contracts provide lot sizes.

## 3.3.1 (2024-12-31)

### New

- `get_funding_history` queries deposit and withdrawal history.
- Bar queries accept `trade_session`.

## 3.3.0 (2024-12-17)

### New

- `get_stock_fundamental` queries stock fundamentals such as ROE and price-to-book ratios.

### Fixed

- Push errors invoke the error callback correctly.

## 3.2.9 (2024-11-25)

### Fixed

- Batch contract queries send the correct parameters.

## 3.2.8 (2024-11-11)

### New

- Order queries optionally include commission details through `show_charges`.
- Prime-account assets provide uncollected amounts and locked funds.
- Position push messages provide position and saleable quantities.

## 3.2.7 (2024-07-12)

### New

- Positions provide quantity, saleable quantity, daily profit/loss, previous close, and related fields.

## 3.2.6 (2024-07-03)

### Fixed

- Option-depth responses decode correctly.

## 3.2.5 (2024-06-19)

### New

- `get_option_depth` queries option depth.
- `get_option_symbols` queries option symbols.
- Option chains, quotes, and expiration queries accept a market.

## 3.2.4 (2024-06-05)

### New

- Orders support overnight trading through `trading_session_type`.
- Positions provide maintenance-margin value and percentage.

## 3.2.3 (2024-04-11)

### Fixed

- Option-expiration DataFrame columns are handled correctly for multiple symbols.

## 3.2.2 (2024-04-09)

### New

- Push connections support complete tick data.
- Open-order and filled-order queries accept result limits.

## 3.2.1 (2024-04-09)

### Fixed

- Option quotes include the change value.

## 3.2.0 (2024-04-02)

### New

- Option-chain queries accept `return_greek_value`.

### Breaking

- Managed-account queries no longer insert a default account when the account parameter is omitted.

## 3.1.9 (2024-03-18)

### New

- Push connections support minute bars.
- Option expirations include cycle information.

### Changed

- Option-chain filters use improved defaults.

## 3.1.8 (2024-03-12)

### New

- Orders support fractional quantities through `quantity_scale`.

### Fixed

- Tick-size price adjustment supports `CLOSED_OPEN` intervals.

## 3.1.7 (2024-02-28)

### Fixed

- Order-push commission and fee values revert from double to float.

## 3.1.6 (2024-02-26)

### New

- Orders and order push messages provide GST.

### Changed

- Order-push commission and fee values use double precision instead of float.

## 3.1.5 (2024-01-19)

### Fixed

- Protobuf message framing no longer prevents push connections from being established.

## 3.1.4 (2024-01-19)

### Changed

- HTTP requests reuse connections, and RSA signing is more efficient.

## 3.1.3 (2024-01-04)

### New

- Symbol-name queries support OTC instruments.
- Prime-account assets accept the `consolidated` option.

### Fixed

- Market-scanner queries honor multi-tag field filters.

## 3.1.2 (2023-11-17)

### New

- Push subscriptions support US option depth.

## 3.1.1 (2023-10-18)

### New

- `oca_order` creates OCA orders.

### Changed

- Timeline queries use API version 3.0 by default.

## 3.1.0 (2023-10-11)

### Fixed

- Option-ranking subscriptions handle enum parameters correctly.

## 3.0.9 (2023-08-29)

### New

- Order responses provide the latest price.

## 3.0.8 (2023-08-16)

### New

- Additional usage examples are available.

## 3.0.7 (2023-08-11)

### New

- Fund APIs support symbol lists, current quotes, history, and contracts.
- Order push messages provide total and filled cash amounts.
- Push clients support custom heartbeat callbacks.

## 3.0.6 (2023-07-31)

### Changed

- Push failures use consistent exception handling.

## 3.0.5 (2023-07-24)

### Fixed

- Partial-fill order push messages convert to the correct status enum.

## 3.0.4 (2023-07-19)

### New

- Symbol queries support OTC instruments through `include_otc`.

### Breaking

- Protobuf order-status callbacks expose `status` as an `OrderStatus` enum-name string. Convert it with `OrderStatus[frame.status]` or `get_order_status(frame.status)`.

## 3.0.3 (2023-07-10)

### New

- Stock quotes can include pre-market and post-market data through `include_hour_trading`.

## 3.0.2 (2023-07-07)

### New

- Option K-line queries accept sort direction.

### Fixed

- Push reconnection works correctly.

## 3.0.1 (2023-06-21)

### New

- Historical K-line quota queries are available.
- Positions provide profit/loss calculated from average prices.
- Push connections support ranking data.

## 3.0.0 (2023-06-08)

### Breaking

- Push connections use Protobuf by default instead of STOMP.

## 2.4.0 (2023-06-07)

### New

- Combination option orders are supported.

### Fixed

- Paginated K-line queries handle empty DataFrames correctly.

## 2.3.9 (2023-06-01)

### New

- Order-status push messages provide user remarks.

### Fixed

- Protobuf tick messages are decompressed correctly.

## 2.3.8 (2023-05-09)

### New

- Contract responses provide discounted-margin information.
- Quote clients query stock-scanner tags.

### Changed

- Stock-scanner fields are updated.

## 2.3.7 (2023-04-18)

### New

- `get_estimate_tradable_quantity` estimates tradable quantities.
- Orders provide external IDs.
- Positions and position push messages provide saleable status; queried saleable status is available for A-shares.

## 2.3.6 (2023-04-11)

### New

- Warrant and CBBC queries support filtering and real-time quotes.
- Option bars accept result limits.

## 2.3.5 (2023-03-28)

### New

- Segment-fund APIs support available-fund queries, transfers, cancellation, and history across securities, futures, and funds.
- `place_forex_order` places foreign-exchange orders.
- Option bars accept a period and support minute intervals.

## 2.3.4 (2023-03-20)

### New

- Auction market and auction limit orders are supported.

### Fixed

- Push clients no longer fail with missing-module errors.

## 2.3.3 (2023-03-10)

### New

- Token refresh supports multiple processes through token-file monitoring; install `watchdog` to enable it.

### Fixed

- Calendar queries work correctly.

## 2.3.2 (2023-03-03)

### New

- Push clients optionally support Protobuf through `user_protobuf=True`. Subscription calls remain mostly compatible, but Protobuf callback arguments differ from STOMP callback arguments.

## 2.3.1 (2023-02-23)

### New

- Two-factor-authentication tokens support configurable refresh intervals; set `token_refresh_duration = 0` to disable automatic refresh.

### Fixed

- Tick push fields decode correctly.
- Token-refresh threads stop when the main process exits.

## 2.3.0 (2023-02-16)

### New

- Properties-file configuration and two-factor-authentication tokens are supported.

## 2.2.9 (2023-02-09)

### Changed

- Requests other than order placement, modification, and cancellation retry up to five times by default. Configure `retry_max_tries`, or set it to zero to disable retries.

### Fixed

- Tick push messages no longer fail during decoding.

## 2.2.8 (2023-02-03)

### Fixed

- Option-identifier helpers handle additional Hong Kong option formats.

## 2.2.7 (2023-01-11)

### New

- Log paths are configurable.

## 2.2.6 (2022-12-14)

### Fixed

- Installation supports Windows systems using GBK encoding.

## 2.2.5 (2022-12-12)

### New

- Contract responses indicate ETF status and leverage.

## 2.2.4 (2022-12-09)

### New

- `get_capital_flow` queries capital flows.
- `get_capital_distribution` queries capital distribution.
- `get_stock_broker` queries Hong Kong broker information.

## 2.2.3 (2022-12-07)

### New

- `market_scanner` provides stock screening.

## 2.2.2 (2022-11-22)

### New

- Orders support GTD time in force.
- Push subscriptions support execution details.

## 2.2.1 (2022-11-07)

### Fixed

- Trade-tick queries honor an explicit zero begin index.

## 2.2.0 (2022-11-01)

### New

- Futures tick subscriptions are available through `subscribe_tick` and `tick_changed`.

## 2.1.9 (2022-10-12)

### New

- License configuration selects the appropriate service addresses.
- Contracts provide short initial and maintenance margins, with `to_str` for displaying all attributes.
- Financial-report queries accept begin and end dates.

### Changed

- Trade-tick queries remain compatible with API version 1.0.

## 2.1.8 (2022-08-26)

### New

- Order queries accept a segment type for securities, futures, or all instruments.

### Changed

- Push clients use updated reconnection retry limits.
- Contract queries use API version 3.0.

### Fixed

- Hong Kong option contract queries return data correctly.

## 2.1.7 (2022-08-19)

### New

- `get_all_future_contracts` queries all contracts for a futures product.
- Attached orders support trailing stops.

### Breaking

- `get_future_trade_ticks` accepts one contract instead of a list.

## 2.1.6 (2022-08-11)

### New

- Client configuration supports a global timezone.

## 2.1.5 (2022-08-01)

### New

- Trading APIs support a configurable global language.

## 2.1.4 (2022-07-18)

### New

- `get_analytics_asset` queries historical asset performance.
- `PriceUtil` adjusts order prices to contract tick sizes.
- Orders provide update times, and order lists can sort by creation or status-update time.
- Position queries accept option expiry, strike, and put/call filters.

## 2.1.3 (2022-07-01)

### New

- Push clients support tick subscriptions and unsubscriptions.
- `query_subscribed_callback` queries current subscriptions.
- Trade-tick queries support pre-market and post-market sessions.

### Changed

- `subscribed_symbols` is deprecated in favor of `query_subscribed_callback`.

## 2.1.2 (2022-06-14)

### Changed

- The STOMP dependency is upgraded from 4.1.24 to 8.0.1.

### Breaking

- `PushClient.auto_reconnect` is removed. Bind a custom `disconnect_callback` to implement custom reconnection.
- A newer connection using the same tigerId can disconnect an earlier connection; the earlier client reports an exception and stops receiving data.

## 2.1.1 (2022-05-25)

### New

- Stock and futures bars support batch pagination through `get_bars_by_page` and `get_future_bars_by_page`.
- Bar queries accept page tokens.
- Orders support user remarks when enabled for the account.

## 2.1.0 (2022-05-07)

### New

- Service addresses are discovered dynamically.
- Option-calculation helpers are available.
- `get_future_contract` queries a futures contract by code.
- `get_derivative_contracts` queries derivatives for an underlying instrument.

## 2.0.9 (2022-04-18)

### New

- `get_timeline_history` queries historical timelines.
- Orders provide attached-order IDs and accept limit-price adjustment bounds.

### Breaking

- Placement, modification, and cancellation return order IDs instead of booleans.
- Quote clients acquire market-data device access automatically. Set `is_grab_permission=False` to disable this and call `grab_quote_permission` explicitly.

## 2.0.7 (2022-01-31)

### Changed

- Default service addresses are updated.

## 2.0.6 (2022-01-24)

### New

- Contracts provide margin eligibility, close-only status, and shortable quantities.
- Orders provide attribute descriptions and order sources.

### Breaking

- `OpenApiRequest` moves from `tigeropen.quote.request` to `tigeropen.common.request`. Update imports accordingly.

## 2.0.5 (2022-01-10)

### New

- `get_quote_permission` queries quote permissions.
- `get_transactions` queries prime-account executions.
- A complete strategy example is available.

### Changed

- Enum parameters also accept their underlying values.
- Order placement no longer validates the returned `Order.order_id` attribute.
- SDK logging defaults to DEBUG instead of INFO.
- Installation no longer pins pandas to one version.

### Breaking

- `grab_quote_permission` responses rename `expireAt` to `expire_at`.

## 2.0.4 (2021-12-08)

### New

- `get_prime_assets` queries prime and paper-account assets.

## 2.0.3 (2021-12-01)

### New

- Option-chain queries support filtering.
- `get_stock_delay_briefs` queries delayed quotes.

## 2.0.2 (2021-11-01)

### Changed

- Removed rarely used client-configuration properties.
- Improved push subscriptions.

## 2.0.1 (2021-09-18)

### Breaking

- Python 2 is no longer supported.

## 1.4.0 (2021-06-28)

### New

- Depth queries and subscriptions are supported.
- Clients can acquire market-data device access.

## 1.2.0 (2020-04-02)

### New

- Industry APIs are available.

## 1.1.10 (2020-01-19)

### New

- Corporate-action calendar data is available.
- Global accounts support attached orders.

## 1.1.9 (2019-10-28)

### Fixed

- Installation issues from version 1.1.8 are resolved.

## 1.1.8 (2019-10-27)

### New

- Position and order APIs provide unique instrument identifiers.
- Option data includes historical volatility for the underlying asset.

## 1.1.7 (2019-08-02)

### New

- Futures quote push messages provide decimal prices.
- Order and position push messages include symbols; account types retain their respective symbol conventions.
- Asset push messages identify the account segment.
- Stock contracts provide margin-trading information.
- Added a strategy example and a configuration-construction helper.

## 1.1.6 (2019-07-12)

### New

- Position, order, and asset subscriptions can target a specific account.

## 1.1.5 (2019-06-27)

### New

- `get_contracts` queries contracts in batches.
- Quote subscriptions can select trades or quotes.
- Push timestamps are delivered as needed without a separate subscription.

### Changed

- Asset queries distinguish securities and futures accounts more clearly.

### Fixed

- Pre-market trade push messages are delivered correctly.

## 1.1.4 (2019-06-06)

### New

- Order lists can include both securities and futures orders.
- `get_order` queries an order by ID.
- Tick queries support multiple stocks.
- Corporate-action APIs provide dividends and splits.
- Fundamental APIs provide daily valuations, financial statements, and derived factors.
- Filled, pending-cancellation, and cancelled-order lists are available.
- Push connections support minute timelines and heartbeats.
- Futures queries support additional bar periods.

### Changed

- Order creation no longer requires separate contract or order-ID requests.
- Push order statuses use `OrderStatus` objects.

### Fixed

- Quote subscriptions honor selected fields.
- Futures one-minute bars are queried correctly.
- Order queries honor the security type.
