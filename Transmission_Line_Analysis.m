clear;
clc;
close all;
%% --- Parameters ---
Z0 = 50; % Characteristic Impedance (Ohms)
L = 1.0; % Length of the transmission line (meters)
f = 300e6; % Operating Frequency (300 MHz)
V_plus = 1; % Amplitude of the forward-traveling voltage wave (Volts)
%% --- Calculations ---
c = 3e8; % Speed of light (m/s)
lambda = c / f; % Wavelength (m)
beta = 2 * pi / lambda; % Propagation constant (rad/m)
% Position vector along the line (from load z=0 to source z=L)
z = linspace(0, L, 500);
% Define Load Conditions
load_cases = {
'Matched Load', Z0;
'Short Circuit', 0;
'Open Circuit', 1e9; % Using a very large number for open circuit
'Complex Load', 30 + 1j*40
};
num_cases = size(load_cases, 1);
%% --- Plotting ---
figure('Name', 'Transmission Line Analysis', 'NumberTitle', 'off', 'Color', 'w');
for i = 1:num_cases
load_name = load_cases{i, 1};
ZL = load_cases{i, 2};
% Calculate Reflection Coefficient
Gamma = (ZL - Z0) / (ZL + Z0);
% Calculate Voltage and Current along the line
% Note: z is measured from the load
Vz = V_plus * (exp(1j * beta * z) + Gamma * exp(-1j * beta * z));
Iz = (V_plus / Z0) * (exp(1j * beta * z) - Gamma * exp(-1j * beta * z));
% Calculate VSWR
VSWR = (1 + abs(Gamma)) / (1 - abs(Gamma));
% Plot Voltage Standing Wave
subplot(num_cases, 2, 2*i - 1);
plot(z, abs(Vz), 'b-', 'LineWidth', 1.5);
grid on;
title(['Voltage Wave: ', load_name]);
xlabel('Distance from Load (m)');
ylabel('|V(z)| (Volts)');
ylim([0, V_plus * (1 + abs(Gamma)) * 1.1]);
text(0.1, V_plus * (1 + abs(Gamma)) * 0.9, ['VSWR = ', num2str(VSWR, '%.2f')]);
% Plot Current Standing Wave
subplot(num_cases, 2, 2*i);
plot(z, abs(Iz), 'r-', 'LineWidth', 1.5);
grid on;
title(['Current Wave: ', load_name]);
xlabel('Distance from Load (m)');
ylabel('|I(z)| (Amps)');
ylim([0, (V_plus / Z0) * (1 + abs(Gamma)) * 1.1]);
end
sgtitle('Voltage and Current Standing Waves for Various Terminations', 'FontSize', 14, 'FontWeight', 'bold');