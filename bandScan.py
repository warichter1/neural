# -*- coding: utf-8 -*-
"""
Evpanding: Estimate Relaxation from Band Powers
Added Gamma and built out class: GetWaves to track 4 relaxation and Gamma waves
From muselsl examples
Repository: https://github.com/alexandrebarachant/muse-lsl

This example shows how to buffer, epoch, and transform EEG data from a single
electrode into values for each of the classic frequencies (e.g. alpha, beta, theta)
Furthermore, it shows how ratios of the band powers can be used to estimate
mental state for neurofeedback.

The neurofeedback protocols described here are inspired by
*Neurofeedback: A Comprehensive Review on System Design, Methodology and Clinical Applications* by Marzbani et. al

Adapted from https://github.com/NeuroTechX/bci-workshop
"""

import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from matplotlib.font_manager import FontProperties
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
import utils  # Our own utility functions

# Handy little enum to make code more readable


class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3
    Gamma = 4


""" EXPERIMENTAL PARAMETERS """
class Parameters:   
    """Modify these to change aspects of the signal processing."""  
    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    BUFFER_LENGTH = 5   
    # Length of the epochs used to compute the FFT (in seconds)
    EPOCH_LENGTH = 1    
    # Amount of overlap between two consecutive epochs (in seconds)
    OVERLAP_LENGTH = 0.8  
    # Amount to 'shift' the start of each next consecutive epoch
    SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
    # Index of the channel(s) (electrodes) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    INDEX_CHANNEL = [0]

class GetWaves:
    def __init__(self, timeout=2):       
        """ 1. CONNECT TO EEG STREAM """
        # params = Parameters
        bufferLength = Parameters.BUFFER_LENGTH
        self.epochLength = Parameters.EPOCH_LENGTH
        self.shiftLength = Parameters.SHIFT_LENGTH
        
        # Search for active LSL streams
        print('Looking for an EEG stream...')
        streams = resolve_byprop('type', 'EEG', timeout=timeout)
        if len(streams) == 0:
            raise RuntimeError('Can\'t find EEG stream.')

        # Set active EEG stream to inlet and apply time correction
        print("Start acquiring data")
        self.inlet = StreamInlet(streams[0], max_chunklen=12)
        eeg_time_correction = self.inlet.time_correction()
    
        # Get the stream info and description
        info = self.inlet.info()
        description = info.desc()
    
        # Get the sampling frequency
        # This is an important value that represents how many EEG data points are
        # collected in a second. This influences our frequency band calculation.
        # for the Muse 2016, this should always be 256
        self.fs = int(info.nominal_srate())
    
        """ 2. INITIALIZE BUFFERS """
    
        # Initialize raw EEG data buffer
        self.eeg_buffer = np.zeros((int(self.fs * bufferLength), 1))
        self.filter_state = None  # for use with the notch filter
    
        # Compute the number of epochs in "buffer_length"
        n_win_test = int(np.floor((bufferLength - self.epochLength) /
                                  self.shiftLength + 1))
    
        # Initialize the band power buffer (for plotting)
        # bands will be ordered: [delta, theta, alpha, beta]
        self.band_buffer = np.zeros((n_win_test, 5))


    def run(self, function=None, params=[None], verbose=False):
        """ 3. GET DATA """
        # The try/except structure allows to quit the while loop by aborting the
        # script with <Ctrl-C>
        print('Press Ctrl-C in the console to break the while loop.')
        plt.ion()
        figure, ax = plt.subplots(figsize=(8,6))
        font = FontProperties(family='ubuntu',
                              weight='bold',
                              style='oblique', size=6.5)
        x=0
        try:
            # The following loop acquires data, computes band powers, and calculates neurofeedback metrics based on those band powers
            while True:
    
                """ 3.1 ACQUIRE DATA """
                # Obtain EEG data from the LSL stream
                eeg_data, timestamp = self.inlet.pull_chunk(
                    timeout=1, max_samples=int(self.shiftLength * self.fs))
    
                # Only keep the channel we're interested in
                ch_data = np.array(eeg_data)[:, Parameters.INDEX_CHANNEL]
    
                # Update EEG buffer with the new data
                self.eeg_buffer, self.filter_state = utils.update_buffer(
                    self.eeg_buffer, ch_data, notch=True,
                    filter_state=self.filter_state)
    
                """ 3.2 COMPUTE BAND POWERS """
                # Get newest samples from the buffer
                data_epoch = utils.get_last_data(self.eeg_buffer,
                                                 self.epochLength * self.fs)
                # Compute band powers
                band_powers = utils.compute_band_powers(data_epoch, self.fs)
                self.band_buffer, _ = utils.update_buffer(self.band_buffer,
                                                     np.asarray([band_powers]))
                self.output(band_powers, verbose)
                handles = []
                label, = ax.plot(x, band_powers[Band.Delta], label='Delta')
                handles.append(label)
                label, = ax.plot(x, band_powers[Band.Theta], label='Theta')
                handles.append(label)
                label, = ax.plot(x, band_powers[Band.Alpha], label='Alpha')
                handles.append(label)
                label, = ax.plot(x, band_powers[Band.Beta], label='Beta')
                handles.append(label)
                label, = ax.plot(x, band_powers[Band.Gamma], label='Gamma')
                handles.append(label)
                plt.title('Brain Waves')
                plt.legend(handles=handles, prop=font)
                figure.canvas.draw()
                figure.canvas.flush_events()
                figure.show() 
                x += 1
                if function is not None:
                    function(params)
                    
            plt.show(block=True)
        except KeyboardInterrupt:
            print('Closing!')
            
    def smoothBandPowers(self):
        """smooth_band_powers."""
        return np.mean(self.band_buffer, axis=0)
    
    def output(self, bands, verbose):
                print('Delta: ', bands[Band.Delta], 
                      ' Theta: ', bands[Band.Theta],
                      ' Alpha: ', bands[Band.Alpha], 
                      ' Beta: ', bands[Band.Beta],
                      'Gamma:', bands[Band.Gamma])
                # Compute the average band powers for all epochs in buffer
                # This helps to smooth out noise
                smooth_band_powers = self.smoothBandPowers()
    
                if verbose:
                    """ 3.3 COMPUTE NEUROFEEDBACK METRICS """
                    # These metrics could also be used to drive brain-computer interfaces
        
                    # Alpha Protocol:
                    # Simple redout of alpha power, divided by delta waves in order to rule out noise
                    alpha_metric = smooth_band_powers[Band.Alpha] / \
                        smooth_band_powers[Band.Delta]
                    print('Alpha Relaxation: ', alpha_metric)
        
                    # Beta Protocol:
                    # Beta waves have been used as a measure of mental activity and concentration
                    # This beta over theta ratio is commonly used as neurofeedback for ADHD
                    beta_metric = smooth_band_powers[Band.Beta] / \
                        smooth_band_powers[Band.Theta]
                    print('Beta Concentration: ', beta_metric)
        
                    # Gamma Protocol:
                    # Gamma waves are associated with cognitive processing, Learning and memory
                    # Gamma waves are fast rhythms that are responsible for the brain’s neural 
                    # connections and data transfer to the outside world.
                    gamma_metric = smooth_band_powers[Band.Gamma] # / \
                        #smooth_band_powers[Band.Theta]
                    print('Gamma Perception: ', gamma_metric)
                    
                    # Alpha/Theta Protocol:
                    # This is another popular neurofeedback metric for stress reduction
                    # Higher theta over alpha is supposedly associated with reduced anxiety
                    theta_metric = smooth_band_powers[Band.Theta] / \
                        smooth_band_powers[Band.Alpha]
                    print('Theta Relaxation: ', theta_metric)
    

if __name__ == "__main__":
    print("Activating")
    waves = GetWaves()
    waves.run()
    