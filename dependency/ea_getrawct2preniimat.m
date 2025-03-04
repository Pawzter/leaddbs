function [tmat,postopct] = ea_getrawct2preniimat(options,inverse)
% Gets the transformation from options.prefs.rawctnii_unnormalized to
% options.prefs.prenii_unnormalized and extracts the transformation matrix
%
% Returns: transformation matrix in LPI- (= RAS+)
%
% 2018, Andreas Husch, University of Luxembourg, Intenventional
% Neuroscience Group

if ~exist('inverse','var')
    inverse=0;
end

directory=[options.root,options.patientname,filesep];

switch options.prefs.reco.mancoruse
    case 'postop'
        try
            load([directory 'ea_coregctmethod_applied.mat']);
        catch
            tmat=eye(4);
            postopct=[directory,options.prefs.ctnii_coregistered];
            return
        end
        postopct=[directory,options.prefs.rawctnii_unnormalized];

        switch coregct_method_applied{end}
            case {'ea_coregctmri_ants','ea_coregctmri_ants_refine'}
                if inverse
                    antsmts=dir([directory,ea_stripext(options.prefs.prenii_unnormalized),'2',ea_stripext(options.prefs.rawctnii_unnormalized),'_ants*','.mat']);
                else
                    antsmts=dir([directory,ea_stripext(options.prefs.rawctnii_unnormalized),'2',ea_stripext(options.prefs.prenii_unnormalized),'_ants*','.mat']);
                end
                t=load([directory,antsmts(end).name]);
                % The affine field name in tfields{1} differs depending on the ants call, its often
                % "AffineTransform_float_3_3", but alternativley "AffineTransform_double_3_3"
                % or "CompositeTransform_double_3_3" could occour. Note that composite
                % transforms would need further handling (multipling of the resulting
                % matrices) as they store multiple ants transforms in one file *wihthout* combining them directly.
                tfields = fieldnames(t);
                % affine         % fixed
                tmat=ea_antsmat2mat(t.(tfields{1}),t.(tfields{2}));
            case 'ea_coregctmri_brainsfit'
                if inverse
                    reg2org.fixed = h5read([directory,ea_stripext(options.prefs.rawctnii_unnormalized),'2',ea_stripext(options.prefs.prenii_unnormalized),'_brainsfit_Inverse.h5'],'/TransformGroup/0/TranformFixedParameters');
                    reg2org.AffineTransform_float_3_3 = h5read([directory ea_stripext(options.prefs.rawctnii_unnormalized),'2',ea_stripext(options.prefs.prenii_unnormalized),'_brainsfit_Inverse.h5'],'/TransformGroup/0/TranformParameters');
                else
                    reg2org.fixed = h5read([directory,ea_stripext(options.prefs.rawctnii_unnormalized),'2',ea_stripext(options.prefs.prenii_unnormalized),'_brainsfit.h5'],'/TransformGroup/0/TranformFixedParameters');
                    reg2org.AffineTransform_float_3_3 = h5read([directory ea_stripext(options.prefs.rawctnii_unnormalized),'2',ea_stripext(options.prefs.prenii_unnormalized),'_brainsfit.h5'],'/TransformGroup/0/TranformParameters');
                end
                tmat = ea_antsmat2mat(reg2org.AffineTransform_float_3_3,reg2org.fixed);
            case 'ea_coregctmri_fsl'
                tmat_flirt = dlmread([directory 'anat_t12postop_ct_flirt1.mat']);
                %TODO check if add + 1 is nessesary, check the inverse case
                tmat = flirtmat2worldmatPaCER(tmat_flirt, [directory,options.prefs.prenii_unnormalized],[directory,options.prefs.rawctnii_unnormalized], false );
                %disp(['Warning: Currently, FSL coregistration is not supported. Using registered CT.'])
                %tmat=eye(4);
                %postopct=[directory,options.prefs.ctnii_coregistered];
        end
    case 'rpostop'
        tmat=eye(4);
        postopct=[directory,options.prefs.ctnii_coregistered];
end
