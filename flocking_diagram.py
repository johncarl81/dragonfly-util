#!/usr/bin/env python

import matplotlib.pyplot as plt


def main():


    fig, ax = plt.subplots(figsize=(5, 5))
    params = {'mathtext.default': 'regular' }
    plt.rcParams.update(params)


    ax.text(0, 0, 'test')

    ax.text(1, 10, '$\vec{a}_r =  - \smashoperator{\sum_{\forall i, j \colon i \neq j, \abs{\vec{x}_{i,j}} \leq r_o }{\textsc{min}(r_1, r_0 - \abs{\vec{x}_{i,j}}) \frac{\vec{x}_{i,j}}{\abs{\vec{x}_{i,j}}}}}$')

    ax.axis('off')
    plt.savefig('flocking_details.pdf', dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()
