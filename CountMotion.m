function CarCount = CountMotion(h5fn, key, doplot)
%% CountMotion  load motion data and count vehicles
%
%%% inputs
% * h5fn: HDF5 filename
% * key: HDF5 variable with desired data -- scalartext or cell
% * doplot: show movie of data
%
narginchk(2, 3)
validateattributes(h5fn, {'string','char'}, {'vector'})
if nargin < 3
  doplot = false;
end
validateattributes(doplot, {'logical'}, {'scalar'})

MAX_LANES = 4;

cwd = fileparts(mfilename('fullpath'));
addpath([cwd, filesep, 'matlab'])

%% load motion data
assert(is_file(h5fn), [h5fn, ' is not a file.'])

if isoctave
  if iscell(key)
    x = load(h5fn, key{1});
    y = load(h5fn, key{2});
    motion = hypot(x.(key{1}), y.(key{2}));
  else
    motion = load(h5fn, key);
    motion = abs(motion.(key));
  end
else % matlab
  if iscell(key)
    assert(length(key) == 2, 'specify dx dy')
    x = single(h5read(h5fn, fix_key(key{1})));
    y = single(h5read(h5fn, fix_key(key{2})));
    motion = hypot(x, y);
  else
    motion = abs(single(h5read(h5fn, fix_key(key))));
  end
end

motion = flipud(motion);

%% lane geometry parameters, empirical based on camera perspective w.r.t. traffic
param = read_params([cwd, filesep, 'config.ini']);

frame_count_interval = round(param.video_fps * param.count_interval_seconds);
% approximate elapsed time
time = 0:param.count_interval_seconds:size(motion,3) / param.video_fps + param.count_interval_seconds;

L = size(motion, 2);
iLPF = [round(L*4/9), round(L*5.2/9)];

%% main loop -- 60 fps on Pi Zero !
Nframe = size(motion, 3);
CarCount = zeros(1, length(time));
j = 1;
if doplot
  fg = figure(1); clf(1)
  ax = axes('parent', fg, 'nextplot', 'add');
  h = imagesc(ax, motion(:,:,1));
  set(ax, 'ydir', 'reverse')
  color = {'cyan', 'green', 'white', 'yellow'};
  for m = 1:MAX_LANES
    k = ['lane', sprintf('%d', m)];
    x1 = param.(k);
    if isempty(x1)
      continue
    end
    plot(ax, [1, size(motion,2)], [x1(1), x1(1)], 'color', color{m}, 'linestyle', '--')
    plot(ax, [1, size(motion,2)], [x1(2), x1(2)], 'color', color{m}, 'linestyle', '--')
  end
end
tic
for i = 1:Nframe
  for m = 1:MAX_LANES
    k = ['lane', sprintf('%d', m)];
    N(m) = spatial_discrim(motion(:,:,i), param.(k), iLPF, param.detect_min); %#ok<AGROW>
  end
  if mod(i, frame_count_interval) == 0
    CarCount(j) = sum(N);
    j = j + 1;
  end
  if doplot
    set(h, 'cdata', motion(:,:,i))
    pause(0.1)
  end
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

% lane indices were chosen in zero-based Python
ilane = max(ilane+1, 1);
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


function key = fix_key(key)
%% Matlab wants "/foo" while Octave wants "foo"
validateattributes(key, {'string', 'char'}, {'vector'})

if isoctave
  if strcmp(key(1), '/')
    key = key(2:end);
  end
else
  if ~strcmp(key(1), '/')
    key = ['/', key];
  end
end

end