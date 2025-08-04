classdef WindTurbineModel
    properties
        raio_pas_aerogerador % Raio das pás do rotor
        velocidade_vento % Velocidade do vento
    end

    methods
        function [Cp, lamb_i, lamb] = Model_Cp(obj, velocidade_vento, beta, omega, c1, c2, c3, c4, c5, c6, c7, c8, c9)
            % COEFICIENTE DE PERFORMANCE
            % Cp, lambda, lambda_i calculation

            if nargin < 2 || isempty(velocidade_vento)
                velocidade_vento = obj.velocidade_vento;
            end
            if nargin < 3 || isempty(omega) || omega <= 0
                omega = 0.01;
            end
            
            % Calcula lambda e lambda_i
            lamb = (omega * obj.raio_pas_aerogerador) / velocidade_vento;
            lamb_i = 1 / ( (1 / (lamb + c8 * beta)) - (c9 / (beta^3 + 1)) );

            % Calcula Cp
            Cp = c1 * ((c2 / lamb_i) - (c3 * beta) - (c4 * beta * c5) - c6) * exp(-c7 / lamb_i);
            Cp = max(Cp, 0); % Garante que Cp seja não-negativo

            % Retorna os valores
            return
        end

        function [Cp, lamb_i, lamb] = Cp_Heier(obj, velocidade_vento, beta, omega)
            % Heier (2014) - Eficiência aerodinâmica
            % Parâmetros fixos para o método de Heier e Raiambal
            
            c1 = 0.5; c2 = 116; c3 = 0.4; c4 = 0; c5 = 0;
            c6 = 5; c7 = 21; c8 = 0.08; c9 = 0.035;

            % Chama a função Model_Cp com parâmetros específicos
            [Cp, lamb_i, lamb] = obj.Model_Cp(velocidade_vento, beta, omega, c1, c2, c3, c4, c5, c6, c7, c8, c9);
            return
        end
    end
end
