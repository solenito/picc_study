% Function to evaluate the compliance offset curves as per ASTM Method 
function [Xseg_l,Coffset_l,Xseg_ul,Coffset_ul]=...
    complianceOffset(Xl,Yl,Xul,Yul,Xl_min,X_max,Xul_min,params,opt)
% ---------------
% Inputs
% X is the cyclic load (force, stress, etc)
% Y is the cyclic deformation (displacement, strain, etc)
% subscript l corresponds to the loading portion of the cycle
% subscript ul corresponds to the unloading portion of the cycle
% Xl_min to Xl_max represents the loading range
% Xl_max to Xul_min represents the unloading range
% params = [span shift shift1 HL F] - parameters for compliance offset
% calculation. Default values: [0.10 0.05 0.01 1.0 0.25]
% opt = 1 or 2. If opt = 1, calculate compliance offset curves for loading
% portion of the cycle only. If opt = 2, calculate for both loading and
% unloading portions of the cycle.
% ---------------
% Outputs
% Xseg is a vector of midpoint values of X for the overlapping segments
% Coffset is the % compliance offset of the segments relative to the open
% crack compliance
% subscripts l and ul refer to the loading and unloading portions of the
% cycle
%
% ---------------
%
% Assign calculation parameters
% The instantaenous compliance is obtained using overlapping segments
% More refined segments are used near the minimum load.
span = params(1); shift = params(2); % As a fraction of full load range
shift1 = params(3); % Improved ASTM method (Chung, Song, 2009)
% The open crack compliance is calculated using a least squares linear fit 
% to the top unloading portion of the cycle.
% High and low limits for the top portion
HL = params(4); F = params(5); LL = HL-F;
%
% ---------------
%
% Open crack compliance calculation
% Find indices in the selected range
idx_ul = find(Xul>=(Xul_min+LL*(X_max-Xul_min)) & ...
              Xul<=(Xul_min+HL*(X_max-Xul_min)));
% Perform linear regression
coeffs = polyfit(Xul(idx_ul),Yul(idx_ul),1);
% Scaled open crack compliance (this must be multiplied by appropriate
% constants to obtain the actual open crack compliance)
C0 = coeffs(1);
%
% ---------------
%
% Instantaenous compliance of overlapping segments
for i = 1:opt % Repeat the process of the loading and unloading curves 
    if i==1
        X=Xl; Y=Yl; X_min=Xl_min; % Analyse loading curve first
        if X(1) > X_min % Part of previous cycle included in loading curve
            [~,istart] = min(abs(X-X_min));
            X = X(istart:end);
            Y = Y(istart:end);
        end
    else
        X=Xul; Y=Yul; X_min=Xul_min; % Analyse unloading curve next (if requested by user, opt == 2)
    end

    N_segments = 2+floor((1-span)/shift); % No. of segments
    if mod(span,shift) == 0 % span is a multiple of shift
        N_segments = N_segments-1;
    end
    Range = X_max-X_min; % Total range
    Width = Range*span; % Segment width
    % Midpoints of intermediate segments
    X_mid = X_min+Range*[0.5*span, 0.5*span+(shift:shift:(N_segments-2)*shift), 1-0.5*span]';

    C1 = zeros(N_segments,1); % vector of segment compliances
    for j = 1:N_segments
        idx_seg = X>=X_mid(j)-0.5*Width & X<= X_mid(j)+0.5*Width;
        % Perform linear regression
        coeffs_seg = polyfit(X(idx_seg),Y(idx_seg),1);
        % Scaled instantaenous crack compliance
        C1(j) = coeffs_seg(1);
    end
    % Percentage compliance offset 
    Coffset1 = (C0-C1)*100/C0; 
    
    % Improved ASTM method (Chung, Song, 2009)
    % finer shift between two segments closest to minimum load
    X_mid_fine = [X_mid(1):Range*shift1:X_mid(2)]';
    C2 = zeros(length(X_mid_fine),1); % vector of segment compliances
    for k = 1:length(X_mid_fine)
        idx_seg_fine = X>=X_mid_fine(k)-0.5*Width & X<= X_mid_fine(k)+0.5*Width;
        coeffs_seg_fine = polyfit(X(idx_seg_fine),Y(idx_seg_fine),1);
        C2(k) = coeffs_seg_fine(1);
    end
    % Percentage compliance offset 
    Coffset2 = (C0-C2)*100/C0;
    % Extrapolate compliance offset C2 to Xmin 
    coeff_extrap = polyfit(Coffset2,X_mid_fine,1);
    Coffset_Xmin = (X_min-coeff_extrap(2))/coeff_extrap(1);
    
    % Combine all compliance offset results
    Coffset = [Coffset_Xmin Coffset2' Coffset1(3:end)']';
    Xseg = [X_min X_mid_fine' X_mid(3:end)']';

    if i ==1
        Xseg_l=Xseg; Coffset_l = Coffset;
    else
        Xseg_ul=Xseg; Coffset_ul = Coffset;
    end
end
if opt == 1
    Xseg_ul = NaN; Coffset_ul = NaN;
end
end