#pragma once

#include <cstdint>
#include <type_traits>

#include "core/image.h"
#include "core/image_type_traits.h"
#include "core/pixel_types.h"
#include "core/vector_field.h"
#include "core/grid.h"
#include "interp/map_polynomial.h"

namespace openpiv::windef
{
    using namespace openpiv::core;

    template<
        template <typename> class ImageT,
        typename ContainedT,
        typename ValueT = typename ContainedT::value_t,
        typename = typename std::enable_if_t<
            is_imagetype_v<ImageT<ContainedT>> &&
            is_real_mono_pixeltype_v<ContainedT> &&
            std::is_same_v<ValueT,double>
        >
    >
    void create_deformation_field(
        const image<ContainedT>& frame,
        const grid_coords& field_grid,
        const grid_data& field_data
    )
    {
    
    }

}