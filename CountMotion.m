function Ncount = CountMotion(h5fn, key)
%% CountMotion  load motion data and count vehicles
%
%%% inputs
% * h5fn: HDF5 filename
% * key: HDF5 variable with desired data
%
narginchk(2,2)
validateattributes(h5fn, {'string','char'}, {'vector'})
validateattributes(key, {'string','char'}, {'vector'})

MAX_LANES = 4;

cwd = fileparts(mfilename('fullpath'));
addpath([cwd, filesep, 'matlab'])

%% load motion data
assert(is_file(h5fn), [h5fn, ' is not a file.'])

if isoctave
  if strcmp(key(1), '/')
    % Matlab wants "/foo" while Octave wants "foo"
    key = key(2:end);
  end
  motion = load(h5fn, key);
  motion = motion.(key);
else % matlab
  motion = h5read(h5fn, key);
end

%% lane geometry parameters, empirical based on camera perspective w.r.t. traffic
param = read_params([cwd, filesep, 'config.ini']);

L = size(motion, 2);
iLPF = [round(L*4/9), round(L*5/9)];

%% main loop -- 60 fps on Pi Zero !
Nframe = size(motion, 3);
Ncount = zeros(1,Nframe);
tic
for i = 1:Nframe
  for j = 1:MAX_LANES
    k = ['lane', sprintf('%d', j)];
    N(j) = spatial_discrim(motion(:,:,i), param.(k), iLPF, param.detect_min); %#ok<AGROW>
  end
  Ncount(i) = sum(N);
end

disp(['processed output at ', num2str(Nframe / toc, '%0.1f'), ' fps.'])

end


function N = spatial_discrim(mot, ilane, iLPF, detect_min)
%% countlanes  count automobiles in each lane
%
%%% inputs
% * mot: 2-D image of motion magnitude
% * ilanes: N x 2 pixel "upper / lower" boundaries for each lane
% * iLPF: spatial low pass filter indices
% * minv: power detection threshold
%
% Automobile are big and move fast usually, staying in the same lane
% typically in the field of view.
%
narginchk(4,4)
validateattributes(mot, {'numeric'}, {'real', '2d'})
if isempty(ilane)
  N = 0;
  return
end
validateattributes(ilane, {'numeric'}, {'integer', 'positive', 'numel', 2})
validateattributes(iLPF, {'numeric'}, {'integer', 'positive', 'numel', 2})
validateattributes(detect_min, {'numeric'}, {'real', 'scalar', 'nonnegative'})

%% average motion over lane width
lane = sum(mot(ilane(1):ilane(2), :), 1);
%% compute spatial spectral power
Flane = fftshift(abs(fft(lane)).^2);
%% integrate low frequency power
M = sum(Flane(iLPF(1):iLPF(2)));
%% if low frequency signal is strong enough, declare detection
N = single(detect_min <= M);

end


function p = read_params(fn)
%% this is an overly simple way to parse an .ini file, ignoring section names

assert(is_file(fn), [fn, ' is not a file.'])

fid = fopen(fn);

p = struct();
while ~feof(fid)
  [k, v] = strtok(fgetl(fid), '=');
  if isempty(v)
    continue
  end
  % numeric of up to length 3
  p.(strtrim(k)) = sscanf(v(2:end), '%f,%f,%f');
end

fclose(fid);

end
