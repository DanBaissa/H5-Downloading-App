import h5py
import matplotlib.pyplot as plt
import numpy as np

filename = "F:/test/VNP46A2.A2022152.h22v07.001.2022165090133.h5"

with h5py.File(filename, "r") as f:
    data_fields = f["/HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields"]

    dnb_brdf_corrected_ntl = data_fields['DNB_BRDF-Corrected_NTL'][...]
    gap_filled_dnb_brdf_corrected_ntl = data_fields['Gap_Filled_DNB_BRDF-Corrected_NTL'][...]

    # Perform a log transform on the data. The np.log1p function is used to avoid taking the log of zero.
    dnb_brdf_corrected_ntl = np.log1p(dnb_brdf_corrected_ntl)
    gap_filled_dnb_brdf_corrected_ntl = np.log1p(gap_filled_dnb_brdf_corrected_ntl)

    fig, axs = plt.subplots(2, 1, figsize=(12, 12))

    axs[0].imshow(dnb_brdf_corrected_ntl, cmap='gray')
    axs[0].set_title('Log Transformed DNB_BRDF-Corrected_NTL')

    axs[1].imshow(gap_filled_dnb_brdf_corrected_ntl, cmap='gray')
    axs[1].set_title('Log Transformed Gap_Filled_DNB_BRDF-Corrected_NTL')

    plt.show()
