
function motdet(datadir, duration)
%% motdet  command camera to output and save motion vectors
% 
%%% inputs
% * datadir: directory to use for data storage
% * duration: (seconds) to measure motion

validateattributes(datadir, {'string','char'}, {'vector'})
validateattributes(duration, {'numeric'}, {'real','nonnegative', 'scalar'})

%% Run Picamera code to get motion vectors
cmd = ["python3 motdet.py ",datadir, " ", num2str(duration)];

[serr, sout] = system(cmd);

disp(sout)

end
