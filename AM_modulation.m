clc; clear all; close all;

% AM signal formation
Ac=1; % carrier amplitude
fc=0.5; % carrier frequency
Am=1; % message signal amplitude
fm=0.05; % message signal frequency
Fs=100; % sampling rate/frequency

t=0:0.1:50; % defining the time range & disseminating it into samples
ct=Ac*cos(2*pi*fc*t); % defining the carrier signal wave
mt=Am*cos(2*pi*fm*t); % defining the message signal

subplot(5,1,1); % plotting the message signal wave
plot(mt);
ylabel('Message signal');
subplot(5,1,2); % plotting the carrier signal wave
plot(ct);
ylabel('Carrier');

% under modulation
ka=0.5; % Amplitude sensitivity
AM=ct.*(1+ka*mt); % Amplitude modulated wave, according to the standard definition

subplot(5,1,3); % plotting the amplitude modulated wave
plot(AM);
ylabel('AM: Under mod');

% perfect modulation
ka=1; % Amplitude sensitivity
AM=ct.*(1+ka*mt); % Amplitude modulated wave, according to the standard definition

subplot(5,1,4); % plotting the amplitude modulated wave
plot(AM);
ylabel('AM: Perfect mod');

% over modulation
ka=3; % Amplitude sensitivity
AM=ct.*(1+ka*mt); % Amplitude modulated wave, according to the standard definition

subplot(5,1,5); % plotting the amplitude modulated wave
plot(AM);
ylabel('AM: Over mod');
