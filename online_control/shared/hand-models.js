export const A32_MODEL_IDS = Object.freeze(['TsenseI_v3_2', 'TsenseI_v3_2_withid']);
export const isA32Model = model => A32_MODEL_IDS.includes(model);
export const isA3Model = model => isA32Model(model);
