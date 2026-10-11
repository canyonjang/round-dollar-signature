## T1 Revised Table 1 (coefficients in pp, SE in parentheses)
                               term (1) Baseline    (2) + day FE (3) issuer x size x day FE         (4) value-weighted
                             single        21.44           21.35                      21.42                      37.49
                                         (0.006)         (0.162)                    (0.138)                    (0.546)
                          coin_USDT         0.49            0.53                                                  1.02
                                         (0.006)         (0.160)                                               (0.370)
                         coin_PYUSD         9.10            9.15                                                  3.73
                                         (0.040)         (0.529)                                               (1.394)
                        sz_2_10-100        -0.16           -0.16                                                 -2.52
                                         (0.012)         (0.277)                                               (0.247)
                        sz_3_100-1k         3.53            3.46                                                  1.22
                                         (0.011)         (0.301)                                               (0.237)
                        sz_4_1k-10k         4.65            4.46                                                  2.67
                                         (0.012)         (0.269)                                               (0.241)
                      sz_5_10k-100k         6.03            5.74                                                  4.53
                                         (0.014)         (0.286)                                               (0.290)
                         sz_6_100k+        11.74           11.42                                                 10.83
                                         (0.018)         (0.307)                                               (0.338)
Baseline mean, multi/USDC/$1-10 (%)         7.96                                                                      
 Sample mean whole-dollar share (%)        23.68           23.68                      23.68                      28.11
                      Transfers (N)  186,920,533     186,920,533                186,920,533                185,723,913
                              Cells           36          13,136                     13,136                     13,136
                Issuer FE / size FE          Yes             Yes                   absorbed                        Yes
                             Day FE           No             Yes                   absorbed                        Yes
                            Weights    transfers       transfers                  transfers USD value, excl. mint/burn
                    Standard errors          HC1 clustered (365)            clustered (365)            clustered (365)

## T2 Robustness: single-transfer coefficient (pp), issuer x size x month FE, HC1
                                            sample  coef_pp  se_pp  whole_single_pct  whole_multi_pct  n_transfers  share_of_full_sample_pct
                               Full sample (>= $1)    21.50 0.0060             33.39            11.70    186920533                     100.0
                                   Excl. mint/burn    21.59 0.0060             33.40            11.60    185723913                      99.4
            Excl. exchange & issuer counterparties    22.07 0.0063             33.38            11.07    169671324                      90.8
                     Unlabeled counterparties only    20.66 0.0088             35.88            14.48    108141875                      57.9
        Excl. 1,000 most active senders/recipients    13.70 0.0268             47.08            31.24     39531928                      21.1
                         EOA-to-EOA transfers only     8.57 0.0250             36.65            25.72     82095204                      43.9
       Single = direct wallet call only (vs multi)    25.84 0.0066             37.11            11.70    165992680                      88.8
        Single = contract-mediated only (vs multi)     7.14 0.0094             18.76            11.70    104603076                      56.0
 Strictest: unlabeled, not high-volume, EOA-to-EOA    -8.83 0.0587             48.14            53.02     32841093                      17.6
      Endpoint: EOA-to-EOA, no high-volume address    -8.21 0.0582             48.07            52.29     33151994                      17.7
Endpoint: contract or high-volume address involved    15.34 0.0064             26.66            11.22    152571919                      81.6

## T4 Count- vs value-weighted whole-dollar shares (excl. mint/burn)
 coin  tx_type  n_transfers  count_share_whole_pct  usd_volume_bn  value_share_whole_pct
PYUSD 1_single      1157761                  41.92          45.43                  49.43
PYUSD  2_multi       289049                  14.35          17.56                  16.05
 USDC 1_single     43757223                  28.81        4245.12                  46.95
 USDC  2_multi     57487727                  10.30        6340.98                   9.74
 USDT 1_single     70460960                  30.21        3547.83                  51.54
 USDT  2_multi     50627349                   7.19        2074.38                   5.26
Whole-dollar transfers = 28.11% of USD volume; whole-dollar SINGLE transfers = 23.63% of USD volume.
 tx_type size_bucket  count_share_whole_pct  value_share_whole_pct  usd_volume_share_pct
1_single      0_sub1                   0.00                   0.00                  0.00
1_single      1_1-10                  30.34                  25.34                  0.00
1_single    2_10-100                  28.14                  25.51                  0.01
1_single    3_100-1k                  32.88                  31.32                  0.08
1_single    4_1k-10k                  35.90                  33.89                  0.50
1_single  5_10k-100k                  37.72                  36.69                  1.91
1_single     6_100k+                  45.89                  49.76                 45.67
 2_multi      0_sub1                   0.00                   0.00                  0.00
 2_multi      1_1-10                   7.99                   6.55                  0.00
 2_multi    2_10-100                  10.62                   8.91                  0.00
 2_multi    3_100-1k                  12.86                  10.81                  0.06
 2_multi    4_1k-10k                  11.42                  10.40                  0.42
 2_multi  5_10k-100k                  12.48                  11.65                  1.71
 2_multi     6_100k+                  14.87                   8.53                 49.63

## T3 Counterparty composition (transfers >= $1)
tx_type  cpty_cat cpty_dir  n_transfers  share_of_transfers_pct  share_of_whole_dollar_transfers_pct  whole_dollar_pct  whole_cent_pct  x99_pct  value_weighted_whole_pct
 single unlabeled     none     79132484                   76.65                                82.35             35.88           53.82    0.235                     49.87
 single       cex       to      4936067                    4.78                                 5.05             35.26           55.13    0.218                     60.68
 single       cex     from      4062107                    3.93                                 3.22             27.29           57.36    0.379                     43.96
 single      defi     from      3830184                    3.71                                 1.56             14.01           25.07    0.116                     25.13
 single      defi       to      2993317                    2.90                                 1.06             12.23           15.63    0.034                     13.44
 single     other       to      2704476                    2.62                                 2.26             28.83           50.62    0.196                     59.96
 single     other     from      2700504                    2.62                                 2.30             29.33           43.15    0.139                     71.89
 single    issuer     from       774457                    0.75                                 1.13             50.40           99.10    4.105                     82.27
 single       psp       to       760799                    0.74                                 0.32             14.33           23.94    0.116                     50.97
 single      defi     both       526679                    0.51                                 0.09              5.78            6.64    0.002                     28.30
 single mint_burn     none       298339                    0.29                                 0.28             32.50           47.51    0.334                     99.97
 single       psp     from       297860                    0.29                                 0.08              8.74           13.03    0.051                     63.32
 single    issuer       to       160470                    0.16                                 0.21             44.85           85.98    2.345                     79.10
 single       cex     both        33851                    0.03                                 0.05             46.69           60.02    0.089                     65.40
 single     other     both        17901                    0.02                                 0.02             37.46           45.23    0.084                     49.96
 single    issuer     both        15032                    0.01                                 0.04             94.80           94.91    0.007                     96.80
 single       psp     both          783                    0.00                                 0.00              2.30           93.87    1.149                      0.63
  multi unlabeled     none     29009391                   34.67                                42.92             14.48           22.08    0.104                     24.19
  multi      defi     from     18749349                   22.41                                12.62              6.59            9.13    0.032                      7.48
  multi      defi       to     17877052                   21.36                                19.61             10.74           13.88    0.087                     13.91
  multi       cex     from      6760643                    8.08                                12.57             18.19           23.60    0.121                     42.87
  multi      defi     both      6519836                    7.79                                 4.08              6.12            8.08    0.015                      1.93
  multi     other     from      2005647                    2.40                                 3.05             14.88           16.40    0.068                     33.34
  multi     other       to      1245949                    1.49                                 2.21             17.32           22.62    0.129                     27.97
  multi mint_burn     none       898281                    1.07                                 1.91             20.81           44.03    0.407                     49.01
  multi       cex       to       496312                    0.59                                 0.91             17.86           25.44    0.107                     36.67
  multi     other     both        91904                    0.11                                 0.05              5.06            5.85    0.008                     15.51
  multi       psp     from        10274                    0.01                                 0.01              5.23           99.90    0.827                     48.63
  multi    issuer       to         7184                    0.01                                 0.07             98.86           98.89    0.000                     99.33
  multi       cex     both         3086                    0.00                                 0.01             24.43           32.34    0.000                     89.06
  multi       psp       to          315                    0.00                                 0.00             72.38           90.16    0.635                     67.85

## T3b Transfers INTO payment-processor addresses (invoice settlement) by size
size_bucket      n  n_whole  n_cent  n_x99  whole_dollar_pct  whole_cent_pct  ref_eoa_nonhub_unlabeled_whole_pct
     1_1-10  41842     4008   11178    144              9.58           26.71                               44.04
   2_10-100 377549    34996   63753    372              9.27           16.89                               40.63
   3_100-1k 284673    49917   77145    244             17.53           27.10                               47.00
   4_1k-10k  48505    16707   24256     87             34.44           50.01                               52.96
 5_10k-100k   6158     2361    4317     31             38.34           70.10                               58.00
    6_100k+   2387     1263    1795      4             52.91           75.20                               59.28

## T3c Single transfers by call type and account type
 direct_call  from_contract  to_contract        n  n_whole   n_cent  share_pct  whole_dollar_pct
       False          False        False  1697823   321727   419703       1.64             18.95
       False          False         True  3942114  1667383  1993779       3.82             42.30
       False           True        False  5881309  1332353  2313712       5.70             22.65
       False           True         True  9406607   605524   861774       9.11              6.44
        True          False        False 77117183 28563047 44407451      74.69             37.04
        True          False         True  5198430  1986054  2952699       5.04             38.20
        True           True        False     1834     1085     1564       0.00             59.16
        True           True         True       10        7        7       0.00             70.00

## T6 Single-vs-multi contrast by endpoint type (issuer x size x day FE, day-clustered; excl. mint/burn)
  endpoint  coef_pp  se_pp_day_cluster  whole_single_pct  whole_multi_pct  n_transfers  single_share_pct
eoa_nonhub    -8.14              0.638             48.07            52.29     33151994              97.7
     other    15.26              0.139             26.66            11.22    152571919              46.2

[skip] R04_polygon_cells.csv not found
## T5 Cross-chain replication (Tron/Polygon period as set in R03/R04)
                               chain  coin  n_transfers  single_share_of_transfers_pct  whole_single_pct  whole_multi_pct  lpm_single_pp_sizeFE  se_pp  value_share_whole_pct  single_n_whole_pct  single_n_half_pct  single_n_37_pct  single_n_123456_pct
    ETHEREUM (2025, excl. mint/burn) PYUSD      1446810                           80.0             41.92            14.35                 24.00 0.0959                  40.12                 NaN                NaN              NaN                  NaN
    ETHEREUM (2025, excl. mint/burn)  USDC    101244950                           43.2             28.81            10.30                 19.13 0.0089                  24.66                 NaN                NaN              NaN                  NaN
    ETHEREUM (2025, excl. mint/burn)  USDT    121088309                           58.2             30.21             7.19                 23.89 0.0080                  34.46                 NaN                NaN              NaN                  NaN
ETHEREUM (Jun 2025, excl. mint/burn) PYUSD       118010                           87.1             52.59            14.74                 31.15 0.3879                  55.31                 NaN                NaN              NaN                  NaN
ETHEREUM (Jun 2025, excl. mint/burn)  USDC      6808482                           47.5             29.72            11.23                 19.56 0.0337                  31.35                 NaN                NaN              NaN                  NaN
ETHEREUM (Jun 2025, excl. mint/burn)  USDT      7769452                           63.4             30.66             8.66                 23.81 0.0324                  43.73                 NaN                NaN              NaN                  NaN
                                TRON  USDT    823555852                           98.3             54.99            59.19                -10.50 0.0150                  74.52              54.995             1.8861           0.1599               0.0004
