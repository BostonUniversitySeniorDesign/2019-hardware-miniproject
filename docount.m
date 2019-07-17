function docount(datadir)
%% docount  load motion data and count vehicles
validateattributes(datadir, {'string','char'}, {'vector'})

%% load motion data
h5fn = [datadir, filesep, 'motion.h5'];

assert(exist(h5fn,'file')==2, [h5fn, ' does not exist'])
try
motion = load(h5fn, 'motion');
end
motion = motion.motion;

%% lane geometry parameters, empirical based on camera perspective w.r.t. traffic

ilanes = [25, 27;
          35, 40];
          
L = size(motion, 2);
iLPF = [round(L*4/9), round(L*5/9)];

minv = 500;

%% main loop -- 60 fps on Pi Zero !
Ncount = 0;
%tic
for i = 1:size(motion, 3)
  N = countlanes(motion(:,:,i), ilanes, iLPF, minv);
  Ncount = Ncount + N;
  disp(Ncount)
end
%toc

end
