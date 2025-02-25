function res = extractTs(ds, prevSimTime)
    if nargin == 1; prevSimTime=nan; end

    assert(isa(ds, 'Simulink.SimulationData.Dataset'), 'Not a valid `Dataset` provided.');
    % Package the time and data values of the logged signals into a structure
    ts = simulink.compiler.internal.extractTimeseriesFromDataset(ds);
    for its=1:numel(ts)
        if isfinite(prevSimTime)
            idx = find(ts{its}.Time > prevSimTime);
            % res.(ts{its}.Name).Time = ts{its}.Time(idx);
            % res.(ts{its}.Name).Data = ts{its}.Data(idx);
            es.(ts{its}.Name) = ts{its}.Data(idx);
        else
            % res.(ts{its}.Name).Time = ts{its}.Time;
            res.(ts{its}.Name) = ts{its}.Data;
        end
    end
end