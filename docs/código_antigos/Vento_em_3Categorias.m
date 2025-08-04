close all
clear all
clc


% Definindo o tempo
t = linspace(0, 24, 500);

% Vento médio (Mean wind)
U_mean = 5 + 0.0001 * sin(2 * pi * 0.5 * t);


% Ondas (Waves)
U_waves =  sin(2 * pi * 0.2 * t);
x = linspace(0, 2*pi, length(t)); 
U_waves =  sin( x);

% Turbulência (Turbulence)
% U_turbulence = 2 * (rand(1, length(t)) - 0.5);
U_turbulence = sqrt(-2 * log( rand(1, length(t)) ));


% Fluxo de Ar (Air Flow)
% U_airflow = U_mean + U_waves + U_turbulence;
U_airflow = (U_mean + (U_mean .* U_waves) + (U_mean .* U_turbulence)) / 3;

% Plotando os gráficos
figure;

% Gráfico do vento médio
subplot(2, 3, 1);
plot(t, U_mean, 'LineWidth', 1.5);
title('Vento Médio (Mean Wind)');
xlabel('Tempo (t)');
ylabel('U');
ylim([0 10]);
grid on;

% Gráfico das ondas
subplot(2, 3, 2);
plot(t, U_waves, 'LineWidth', 1.5);
title('Ondas (Waves)');
xlabel('Tempo (t)');
ylabel('U');
grid on;

% Gráfico da turbulência
subplot(2, 3, 3);
plot(t, U_turbulence, 'LineWidth', 1.5);
title('Turbulência (Turbulence)');
xlabel('Tempo (t)');
ylabel('U');
grid on;

% Gráfico do fluxo de ar resultante
subplot(2, 3, [4,5,6]);
plot(t, U_airflow, 'LineWidth', 1.5);
title('Fluxo de Ar (Air Flow)');
xlabel('Tempo (t)');
ylabel('U');
ylim([0 10]);
grid on;

% Ajustar o espaçamento entre os subplots
% sgtitle('Idealização dos Componentes do Vento');
