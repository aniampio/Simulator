import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.style as style
import seaborn as sns
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
# style.use('seaborn-poster') #sets the size of the charts
style.use('ggplot')
# sns.set_context('poster')

plt.rcParams['axes.axisbelow'] = True

def plot():
	''' This function plots how the increasing number of clients (or in other words traffic)
	allows to decrease the additional latency while still providing strong anonymity.
	'''

	stratified_users = [10, 100, 1000, 10000, 100000]
	stratified_anonymity = [11.707888666717338, 12.628707638662362, 12.592305857566098, 12.6282858011491, 12.5083943121997]
	stratified_avg_delay = [100, 10, 1, 0.1, 0.01]

	fig, ax = plt.subplots()

	color1 = 'coral'
	ax.plot(stratified_users, stratified_avg_delay, "-x", color=color1, linestyle=':', markersize=10, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_yticks(stratified_avg_delay)
	ax.set_ylabel("Average delay per mix node [seconds]", color=color1, fontsize=14, labelpad=12)
	ax.tick_params(axis='y', labelcolor=color1, labelsize=12)
	ax.grid()

	ax2 = ax.twinx()
	color = 'darkmagenta'
	ax2.set_ylabel('Anonymity [Entropy]', color=color, fontsize=14, labelpad=12)
	ax2.plot(stratified_users, stratified_anonymity, "-o", color=color, linestyle=':', markersize=10, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2.set_ylim(0, 20)
	ax2.tick_params(axis='y', labelcolor=color, labelsize=12)

	ax.set_xlabel("number of users", fontsize=16, labelpad=12)
	ax.tick_params(axis='x', labelsize=12)
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
	ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))

	plt.title("Nym mixnet: Volume of traffic vs Latency vs Anonymity")

	# ax.grid(False, linestyle="dashed")
	# ax2.grid(False, linestyle="dashed")
	plt.show()


def plot2():

	users = [100, 1000, 10000, 100000]
	p2p_anonymity = [1.7, 1.736641831793427, 1.5352, 1.6859023367489465]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]
	cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]
	multi_cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]

	p2p_latency = [0.303, 0.309806, 0.282375, 0.285564]
	stratified_latency = [0.293462, 0.314276, 0.293368 , 0.299163]
	cascade_batch_latency = [5.387846, 1.455437, 0, 0]
	multi_cascade_batch_latency = [10.629135, 1.907647, 0, 0]

	fig, ax = plt.subplots()
	ax.set_xscale('log')

	color1 = "blue"
	ax.plot(users, p2p_anonymity, "x-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax.plot(users, stratified_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax.plot(users, cascade_batch_anonymity, "v-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax.plot(users, multi_cascade_batch_anonymity, "s-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax.tick_params(axis='y', labelcolor=color1)
	ax.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=14, labelpad=12)

	ax2 = ax.twinx()
	color = 'darkmagenta'
	ax2.set_ylabel('End to End Latency [seconds]', color=color, fontsize=14, labelpad=12)
	ax2.plot(users, p2p_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2.plot(users, stratified_latency, "o-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2.plot(users, cascade_batch_latency, "v-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2.plot(users, multi_cascade_batch_latency, "s-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2.set_ylim(0, 20)
	ax2.tick_params(axis='y', labelcolor=color)


	# Manual legend
	legend_elements = [Line2D([0], [0], marker='x', color="black", label='P2P', alpha=0.7,
	  markerfacecolor='black', markersize=8),
	Line2D([0], [0], marker='o', color="black", label='Stratified', alpha=0.7,
	  markerfacecolor='black', markersize=8),
	  Line2D([0], [0], marker='v', color="black", label='Cascade', alpha=0.7,
	markerfacecolor='black', markersize=8),
	Line2D([0], [0], marker='s', color="black", label='MultiCascade', alpha=0.7,
	  markerfacecolor='black', markersize=8)]
	ax.legend(handles=legend_elements, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
	mode="expand", borderaxespad=0, ncol=4)

	plt.show()


def plot3():
	''' This plot presents how different networks scale with increasing volume of traffic'''

	users = [100, 1000, 10000, 100000]
	p2p_anonymity = [1.7, 1.736641831793427, 1.6614697983186892, 1.6859023367489465]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]
	cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]
	multi_cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]

	p2p_latency = [0.303, 0.309806, 0.282375, 0.285564]
	stratified_latency = [0.293462, 0.314276, 0.293368 , 0.299163]
	cascade_batch_latency = [5.387846, 1.455437, 434.290511, 2*434.290511]
	multi_cascade_batch_latency = [10.629135, 1.907647, 1.511421, 1.464655]

	fig, ax = plt.subplots(2, 2)
	fig.subplots_adjust(wspace=0.5, hspace=0.5)
	ax2 = ax[0, 0]
	ax1 = ax[0, 1]
	ax3 = ax[1, 0]
	ax4 = ax[1, 1]
	ax1.set_xscale('log')
	ax2.set_xscale('log')
	ax3.set_xscale('log')
	ax4.set_xscale('log')

	plt.xlabel("x",labelpad=10)


	# First plot
	color1 = "blue"
	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax1.plot(users, p2p_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax1.set_ylim(0, 20)
	#
	ax1c = ax1.twinx()
	color = 'darkmagenta'
	ax1c.tick_params(axis='y', labelcolor=color)
	ax1c.set_ylabel('End to End Latency [seconds]', color=color, fontsize=10, rotation=270, labelpad=10)
	ax1c.plot(users, p2p_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax1c.set_ylim(0, 20)

	ax1.set_xlabel(' number of users ', fontsize=10)
	ax1.set_axisbelow(True)
	ax1c.set_axisbelow(True)
	ax1c.grid()
	ax1.set_title("P2P Networks", fontsize=10)

	# Second plot
	ax2.tick_params(axis='y', labelcolor=color1)
	ax2.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax2.plot(users, stratified_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax2.set_ylim(0, 20)

	ax2c = ax2.twinx()
	ax2c.tick_params(axis='y', labelcolor=color)
	ax2c.set_ylabel('End to End Latency [seconds]', color=color, fontsize=10, rotation=270, labelpad=10)
	ax2c.plot(users, stratified_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	ax2c.set_ylim(0, 20)

	ax2.set_xlabel(' number of users ', fontsize=10)
	ax2.set_axisbelow(True)
	ax2c.set_axisbelow(True)
	ax2c.grid()
	ax2.set_title("Nym Mixnet", fontsize=10)

	# Third plot
	ax3.tick_params(axis='y', labelcolor=color1)
	ax3.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax3.plot(users, cascade_batch_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax3.set_ylim(0, 20)

	ax3c = ax3.twinx()
	ax3c.tick_params(axis='y', labelcolor=color)
	ax3c.set_ylabel('End to End Latency [seconds]', color=color, fontsize=10, rotation=270, labelpad=10)
	ax3c.set_yscale('log')
	ax3c.plot(users, cascade_batch_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)

	ax3.set_xlabel(' number of users ', fontsize=10)
	ax3.set_axisbelow(True)
	ax3c.set_axisbelow(True)
	ax3c.grid()
	ax3.set_title("Batch and Reorder Cascade", fontsize=10)

	# Fourth plot
	ax4.tick_params(axis='y', labelcolor=color1)
	ax4.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax4.plot(users, multi_cascade_batch_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	ax4.set_ylim(0, 20)

	ax4c = ax4.twinx()
	ax4c.tick_params(axis='y', labelcolor=color)
	ax4c.set_ylabel('End to End Latency [seconds]', color=color, fontsize=10, rotation=270, labelpad=10)
	ax4c.plot(users, multi_cascade_batch_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)

	ax4.set_xlabel(' number of users ', fontsize=10)
	ax4.set_axisbelow(True)
	ax4c.set_axisbelow(True)
	ax4c.grid()
	ax4.set_title("Batch and Reorder MultiCascades", fontsize=10)

	plt.show()

def plot4():

	users = [100, 1000, 10000, 100000]
	p2p_anonymity = [1.7, 1.736641831793427, 1.6614697983186892, 1.6859023367489465]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]

	p2p_anonymity_x1 = [2.9374926952227396, 3.0418098378126626, 2.95215539226739, 2.95215539226739]
	p2p_anonymity_x5 = [5.833688571119568, 6.3651610002095165, 6.6283412926062955, 6.998]
	p2p_anonymity_x10 = [7.049915494197937, 8.198744331314032, 8.638061344421837, 10]

	fig, ax = plt.subplots(nrows=1, ncols=2)
	plt.xlabel("x")
	fig.subplots_adjust(wspace=0.2)
	ax1 = ax[0]
	ax2 = ax[1]

	ax1.set_xscale('log')
	ax2.set_xscale('log')
	ax1.set_xlabel('number of users ', fontsize=10)
	ax2.set_xlabel('number of users ', fontsize=10)

	color1 = "blue"
	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax1.plot(users, stratified_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5, label="Real traffic")
	ax1.set_ylim(0, 20)

	color2 = "mediumvioletred"
	color3 = "tomato"
	color4 = "mediumseagreen"
	ax2.tick_params(axis='y', labelcolor=color1)
	ax2.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=10)
	ax2.plot(users, p2p_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5, label="Real traffic")
	ax2.plot(users, p2p_anonymity_x1, "o-", color=color2, linestyle=':', markersize=8, markeredgecolor=color2, alpha=0.7, markeredgewidth=1.5, label="1:1 [Cover : Real]")
	ax2.plot(users, p2p_anonymity_x5, "o-", color=color3, linestyle=':', markersize=8, markeredgecolor=color3, alpha=0.7, markeredgewidth=1.5, label="5:1 [Cover : Real]")
	ax2.plot(users, p2p_anonymity_x10, "o-", color=color4, linestyle=':', markersize=8, markeredgecolor=color4, alpha=0.7, markeredgewidth=1.5, label="10:1 [Cover : Real]")
	ax2.set_ylim(0, 20)

	ax1.legend(loc="upper right")
	ax2.legend(loc="upper right")
	ax1.set_title("Nym mixnet", fontsize=10)
	ax2.set_title("P2P", fontsize=10)

	plt.show()


def plot5():
	''' Plots the same data as plot4 but comparing only P2P and NYM '''
	users = [100, 1000, 10000, 100000]
	p2p_anonymity = [1.7, 1.736641831793427, 1.6614697983186892, 1.6859023367489465]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]
	# cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]
	# multi_cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]

	p2p_latency = [0.303, 0.309806, 0.282375, 0.285564]
	stratified_latency = [0.293462, 0.314276, 0.293368 , 0.299163]
	# cascade_batch_latency = [5.387846, 1.455437, 434.290511, 2*434.290511]
	# multi_cascade_batch_latency = [10.629135, 1.907647, 1.511421, 1.464655]

	fig1, ax1 = plt.subplots()
	ax1.set_xscale('log')
	plt.xlabel("x",labelpad=10)
	ax1.set_xlabel('number of users ', fontsize=10)

	color1 = "blue"
	color2 = "seagreen"
	ax1.plot(users, p2p_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)
	# ax1.plot(users, stratified_anonymity, "o-", color=color2, linestyle=':', markersize=8, markeredgecolor=color2, alpha=0.8, markeredgewidth=1.5)
	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=14, labelpad=12)
	ax1.set_ylim(0, 20)

	ax2 = ax1.twinx()
	color = 'darkmagenta'
	ax2.set_ylabel('End to End Latency [seconds]', color=color, fontsize=14, labelpad=12)
	ax2.plot(users, p2p_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	# ax2.plot(users, stratified_latency, "x-", color=color2, linestyle=':', markersize=6, markeredgecolor=color2, alpha=0.7, markeredgewidth=1.5)
	ax2.set_ylim(0, 2)
	ax2.tick_params(axis='y', labelcolor=color)
	ax2.grid()



	# Manual legend
	legend_elements = [Line2D([0], [0], marker='o', color=color1, label='P2P Anonymity', alpha=0.7,
	  markerfacecolor=color1, markersize=8),
	# Line2D([0], [0], marker='o', color=color2, label='Nym Anonymity', alpha=0.7,
	#   markerfacecolor=color2, markersize=8),
		  Line2D([0], [0], marker='x', color=color, label='P2P Latency', alpha=0.7,
  	 	  markerfacecolor=color, markersize=8),
		  	 	# Line2D([0], [0], marker='x', color=color2, label='Nym Latency', alpha=0.7,
		  	 	#   markerfacecolor=color2, markersize=8),
				  ]

	ax1.legend(handles=legend_elements, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
	mode="expand", borderaxespad=0, ncol=4)


	plt.show()


def plot6():

	''' Plots the same data as plot4 but comparing only cascade and NYM '''
	users = [100, 1000, 10000, 100000]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]
	cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]

	stratified_latency = [0.293462, 0.314276, 0.293368 , 0.299163]
	cascade_batch_latency = [5.387846, 1.455437, 434.290511, 2*434.290511]

	fig1, ax1 = plt.subplots()
	ax1.set_xscale('log')
	plt.xlabel("x",labelpad=10)
	ax1.set_xlabel('number of users ', fontsize=10)

	color1 = "blue"
	color2 = "seagreen"
	ax1.plot(users, cascade_batch_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.9, markeredgewidth=1.5)
	# ax1.plot(users, stratified_anonymity, "o-", color=color2, linestyle=':', markersize=8, markeredgecolor=color2, alpha=0.9, markeredgewidth=1.5)
	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=14, labelpad=12)
	ax1.set_ylim(0, 20)

	ax2 = ax1.twinx()
	color = 'darkmagenta'
	ax2.set_ylabel('End to End Latency [seconds]', color=color, fontsize=14, labelpad=12)
	ax2.plot(users, cascade_batch_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	# ax2.plot(users, stratified_latency, "x-", color=color2, linestyle=':', markersize=6, markeredgecolor=color2, alpha=0.8, markeredgewidth=1.5)
	ax2.set_yscale('log')
	ax2.set_ylim(0, 100000)
	ax2.tick_params(axis='y', labelcolor=color)
	ax2.grid()


	# Manual legend
	legend_elements = [Line2D([0], [0], marker='o', color=color1, label='Cascade Anonymity', alpha=0.7,
	  markerfacecolor=color1, markersize=8),
	# Line2D([0], [0], marker='o', color=color2, label='Nym Anonymity', alpha=0.7,
	#   markerfacecolor=color2, markersize=8),
		  Line2D([0], [0], marker='x', color=color, label='Cascade Latency', alpha=0.7,
  	 	  markerfacecolor=color, markersize=8),
		  	 	# Line2D([0], [0], marker='x', color=color2, label='Nym Latency', alpha=0.7,
		  	 	#   markerfacecolor=color2, markersize=8),
				  ]

	ax1.legend(handles=legend_elements, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
	mode="expand", borderaxespad=0, ncol=4)


	plt.show()

def plot7():

	''' Plots the same data as plot4 but comparing only multicascade and NYM '''
	users = [100, 1000, 10000, 100000]
	stratified_anonymity = [5.93, 9.314285176247050, 12.6282858011491, 15.794782851545175]
	multi_cascade_batch_anonymity = [9.96578428, 9.96578428, 9.96578428, 9.96578428]

	stratified_latency = [0.293462, 0.314276, 0.293368 , 0.299163]
	multi_cascade_batch_latency = [10.629135, 1.907647, 1.511421, 1.464655]

	fig1, ax1 = plt.subplots()
	ax1.set_xscale('log')
	plt.xlabel("x",labelpad=10)
	ax1.set_xlabel('number of users ', fontsize=10)

	color1 = "blue"
	color2 = "seagreen"
	ax1.plot(users, multi_cascade_batch_anonymity, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.9, markeredgewidth=1.5)
	# ax1.plot(users, stratified_anonymity, "o-", color=color2, linestyle=':', markersize=8, markeredgecolor=color2, alpha=0.9, markeredgewidth=1.5)
	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Anonymity [Entropy]', color=color1, fontsize=14, labelpad=12)
	ax1.set_ylim(0, 20)

	ax2 = ax1.twinx()
	color = 'darkmagenta'
	ax2.set_ylabel('End to End Latency [seconds]', color=color, fontsize=14, labelpad=12)
	ax2.plot(users, multi_cascade_batch_latency, "x-", color=color, linestyle=':', markersize=6, markeredgecolor=color, alpha=0.7, markeredgewidth=1.5)
	# ax2.plot(users, stratified_latency, "x-", color=color2, linestyle=':', markersize=6, markeredgecolor=color2, alpha=0.7, markeredgewidth=1.5)
	ax2.set_ylim(0, 20)
	ax2.tick_params(axis='y', labelcolor=color)
	ax2.grid()


	# Manual legend
	legend_elements = [Line2D([0], [0], marker='o', color=color1, label='MultiCascade Anonymity', alpha=0.7,
	  markerfacecolor=color1, markersize=8),
	# Line2D([0], [0], marker='o', color=color2, label='Nym Anonymity', alpha=0.7,
	#   markerfacecolor=color2, markersize=8),
		  Line2D([0], [0], marker='x', color=color, label='MultiCascade Latency', alpha=0.7,
  	 	  markerfacecolor=color, markersize=8),
		  	 	# Line2D([0], [0], marker='x', color=color2, label='Nym Latency', alpha=0.7,
		  	 	#   markerfacecolor=color2, markersize=8),
				  ]

	ax1.legend(handles=legend_elements, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
	mode="expand", borderaxespad=0, ncol=4)


	plt.show()


def plot8():
	''' This plot shows how the volumes of cover traffic decrease when the number of users increases '''

	users = [100, 500, 1000, 5000, 10000, 50000, 100000]
	cover_traffic = [10, 2, 0.5, 0, 0, 0, 0]

	fig1, ax1 = plt.subplots()
	ax1.set_xscale('log')
	ax1.set_xlabel('number of users ', fontsize=10)
	color1 = "blue"
	ax1.plot(users, cover_traffic, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)

	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Cover traffic \n [cover packets / user in addition to real packets]', color=color1, fontsize=14, labelpad=10)

	ax1.set_title("Cover traffic needed to ensure entropy at least 10", fontsize=10)

	# n = [58, 651, 393, 203, 123, 111, 111]
	# for i, txt in enumerate(n):
	# 	ax1.annotate(txt, (users[i], cover_traffic[i]+0.2))

	plt.show()

def plot9():
	''' This plot shows how the volumes of cover traffic decrease when the number of users increases.
		It is the same as previous plot but with annotations'''

	users = [100, 500, 1000, 5000, 10000, 50000, 100000]
	cover_traffic = [10, 2, 0.8, 0, 0, 0, 0]
	real_traffic = [100, 500, 1000, 5000, 10000, 50000, 100000]
	# 100, 1000, 5K, 10K, 50K, 100K
	anonymity = [1000, 1000, 1000, int(2**10.971285488698075), int(2**12.6282858011491), int(2**14.211534326347138), int(2**15.794782851545175)]

	fig1, ax1 = plt.subplots()
	ax1.set_xscale('log')
	ax1.set_xlabel('number of users ', fontsize=12)
	color1 = "blue"
	ax1.plot(users, cover_traffic, "o-", color=color1, linestyle=':', markersize=8, markeredgecolor=color1, alpha=0.7, markeredgewidth=1.5)

	ax1.tick_params(axis='y', labelcolor=color1)
	ax1.set_ylabel('Cover traffic \n [cover packets / user in addition to real packets]', color=color1, fontsize=12, labelpad=10)

	# ax1.set_title("Cover traffic needed to ensure entropy at least 10", fontsize=14)

	# n = [1000, 1000, 1000, 203, 123, 111, 111]
	for i, txt in enumerate(anonymity):
		ax1.annotate(txt, (users[i], cover_traffic[i]+0.2))

	plt.show()



if __name__ == "__main__":
	plot5()
